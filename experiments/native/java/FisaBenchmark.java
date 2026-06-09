import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Locale;

public final class FisaBenchmark {
    private static final byte[] MAGIC = {'F', 'I', 'S', 'A'};
    private static final int VERSION = 1;
    private static final int MODE_RAW = 0;
    private static final int MODE_SHARED = 1;
    private static Analysis lastAnalysis;

    private static final class Analysis {
        int alphabetSize;
        int symbolWidth;
        int globalMetadataBytes;
        int termThreshold;
        int fullBlocks;
        int thresholdBlocks;
        int sharedBlocks;
        int blockCount;
    }

    private static void writeUvarint(ByteArrayOutputStream out, long value) {
        do {
            int current = (int) (value & 0x7f);
            value >>>= 7;
            out.write(value == 0 ? current : current | 0x80);
        } while (value != 0);
    }

    private static int uvarintLength(long value) {
        int length = 1;
        while ((value >>>= 7) != 0) {
            length++;
        }
        return length;
    }

    private static int sufficientTermThreshold(
        int blockSize, int width, int globalMetadataBytes, int blockCount
    ) {
        int amortized = (globalMetadataBytes + blockCount - 1) / blockCount;
        int threshold = -1;
        for (int terms = 0; terms <= blockSize * 8; terms++) {
            int packed = (terms * width + 7) / 8;
            int payload = uvarintLength(terms) + uvarintLength(packed) + packed;
            int complete = 1 + uvarintLength(blockSize)
                + uvarintLength(payload) + payload + amortized;
            if (complete < blockSize) {
                threshold = terms;
            } else if (threshold >= 0) {
                break;
            }
        }
        return threshold;
    }

    private static long readUvarint(byte[] data, int[] offset) {
        long value = 0;
        int shift = 0;
        while (true) {
            if (offset[0] >= data.length || shift >= 63) {
                throw new IllegalArgumentException("invalid uvarint");
            }
            int current = data[offset[0]++] & 0xff;
            value |= (long) (current & 0x7f) << shift;
            if ((current & 0x80) == 0) {
                return value;
            }
            shift += 7;
        }
    }

    private static List<BigInteger> fibonacciUpTo(BigInteger value) {
        List<BigInteger> fibs = new ArrayList<>();
        fibs.add(BigInteger.ZERO);
        fibs.add(BigInteger.ONE);
        fibs.add(BigInteger.ONE);
        while (fibs.get(fibs.size() - 1).compareTo(value) <= 0) {
            int n = fibs.size();
            fibs.add(fibs.get(n - 1).add(fibs.get(n - 2)));
        }
        return fibs;
    }

    private static List<BigInteger> fibonacciForBlockSize(int blockSize) {
        return fibonacciUpTo(BigInteger.ONE.shiftLeft(blockSize * 8));
    }

    private static int[] gaps(
        byte[] data, int start, int length, List<BigInteger> fibs
    ) {
        if (length == 0) {
            return new int[0];
        }
        byte[] block = Arrays.copyOfRange(data, start, start + length);
        BigInteger remainder = new BigInteger(1, block);
        if (remainder.signum() == 0) {
            return new int[0];
        }
        int index = fibs.size() - 1;
        while (fibs.get(index).compareTo(remainder) > 0) {
            index--;
        }
        int[] indices = new int[(index + 1) / 2 + 1];
        int count = 0;
        while (remainder.signum() != 0) {
            while (fibs.get(index).compareTo(remainder) > 0) {
                index--;
            }
            indices[count++] = index;
            remainder = remainder.subtract(fibs.get(index));
            index -= 2;
        }
        int[] result = new int[count];
        for (int i = 0; i + 1 < count; i++) {
            result[i] = indices[i] - indices[i + 1];
        }
        result[count - 1] = indices[count - 1];
        return result;
    }

    private static byte[] pack(int[] values, int width) {
        if (values.length == 0 || width == 0) {
            return new byte[0];
        }
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        long accumulator = 0;
        int bits = 0;
        for (int value : values) {
            accumulator = (accumulator << width) | value;
            bits += width;
            while (bits >= 8) {
                bits -= 8;
                out.write((int) (accumulator >>> bits) & 0xff);
                accumulator &= bits == 0 ? 0 : (1L << bits) - 1;
            }
        }
        if (bits != 0) {
            out.write((int) (accumulator << (8 - bits)) & 0xff);
        }
        return out.toByteArray();
    }

    private static int[] unpack(byte[] data, int start, int length, int count, int width) {
        int[] values = new int[count];
        if (count == 0 || width == 0) {
            return values;
        }
        long accumulator = 0;
        int bits = 0;
        int output = 0;
        for (int i = start; i < start + length; i++) {
            accumulator = (accumulator << 8) | (data[i] & 0xffL);
            bits += 8;
            while (bits >= width && output < count) {
                bits -= width;
                values[output++] = (int) ((accumulator >>> bits) & ((1L << width) - 1));
                accumulator &= bits == 0 ? 0 : (1L << bits) - 1;
            }
        }
        if (output != count) {
            throw new IllegalArgumentException("truncated packed identifiers");
        }
        return values;
    }

    private static byte[] unsignedBytes(BigInteger value, int length) {
        byte[] signed = value.toByteArray();
        int source = signed.length > 1 && signed[0] == 0 ? 1 : 0;
        int payload = signed.length - source;
        if (payload > length) {
            throw new IllegalArgumentException("decoded integer exceeds block");
        }
        byte[] output = new byte[length];
        System.arraycopy(signed, source, output, length - payload, payload);
        return output;
    }

    public static byte[] encode(byte[] data, int blockSize) {
        int blockCount = (data.length + blockSize - 1) / blockSize;
        List<BigInteger> fibs = fibonacciForBlockSize(blockSize);
        int[][] allGaps = new int[blockCount][];
        Map<Integer, long[]> stats = new HashMap<>();
        long order = 0;
        for (int block = 0; block < blockCount; block++) {
            int start = block * blockSize;
            int length = Math.min(blockSize, data.length - start);
            int[] current = gaps(data, start, length, fibs);
            allGaps[block] = current;
            for (int gap : current) {
                long[] value = stats.get(gap);
                if (value == null) {
                    value = new long[] {0, order++};
                    stats.put(gap, value);
                }
                value[0]++;
            }
        }
        List<Integer> alphabet = new ArrayList<>(stats.keySet());
        alphabet.sort(
            Comparator.<Integer>comparingLong(value -> -stats.get(value)[0])
                .thenComparingLong(value -> stats.get(value)[1])
        );
        Map<Integer, Integer> lookup = new HashMap<>();
        for (int i = 0; i < alphabet.size(); i++) {
            lookup.put(alphabet.get(i), i);
        }
        int width = alphabet.size() <= 1 ? 0 : 32 - Integer.numberOfLeadingZeros(alphabet.size() - 1);
        int globalMetadataBytes = uvarintLength(blockSize)
            + uvarintLength(blockCount)
            + uvarintLength(alphabet.size())
            + 1;
        for (int value : alphabet) {
            globalMetadataBytes += uvarintLength(value);
        }
        int termThreshold = sufficientTermThreshold(
            blockSize, width, globalMetadataBytes, blockCount
        );
        int fullBlocks = 0;
        int thresholdBlocks = 0;
        int sharedBlocks = 0;

        ByteArrayOutputStream body = new ByteArrayOutputStream();
        writeUvarint(body, blockSize);
        writeUvarint(body, blockCount);
        writeUvarint(body, alphabet.size());
        body.write(width);
        for (int value : alphabet) {
            writeUvarint(body, value);
        }
        for (int block = 0; block < blockCount; block++) {
            int start = block * blockSize;
            int length = Math.min(blockSize, data.length - start);
            int[] symbols = new int[allGaps[block].length];
            for (int i = 0; i < symbols.length; i++) {
                symbols[i] = lookup.get(allGaps[block][i]);
            }
            byte[] packed = pack(symbols, width);
            ByteArrayOutputStream transformed = new ByteArrayOutputStream();
            writeUvarint(transformed, symbols.length);
            writeUvarint(transformed, packed.length);
            transformed.write(packed, 0, packed.length);
            byte[] payload = transformed.toByteArray();
            boolean useShared = payload.length < length;
            if (length == blockSize) {
                fullBlocks++;
                if (symbols.length <= termThreshold) {
                    thresholdBlocks++;
                }
            }
            if (useShared) {
                sharedBlocks++;
            }
            body.write(useShared ? MODE_SHARED : MODE_RAW);
            writeUvarint(body, length);
            writeUvarint(body, useShared ? payload.length : length);
            if (useShared) {
                body.write(payload, 0, payload.length);
            } else {
                body.write(data, start, length);
            }
        }

        ByteArrayOutputStream raw = new ByteArrayOutputStream();
        raw.write(MODE_RAW);
        writeUvarint(raw, data.length);
        raw.write(data, 0, data.length);
        ByteArrayOutputStream transformed = new ByteArrayOutputStream();
        transformed.write(MODE_SHARED);
        writeUvarint(transformed, data.length);
        byte[] bodyBytes = body.toByteArray();
        transformed.write(bodyBytes, 0, bodyBytes.length);
        byte[] selected = transformed.size() < raw.size() ? transformed.toByteArray() : raw.toByteArray();

        ByteArrayOutputStream output = new ByteArrayOutputStream();
        output.write(MAGIC, 0, MAGIC.length);
        output.write(VERSION);
        output.write(selected, 0, selected.length);
        Analysis analysis = new Analysis();
        analysis.alphabetSize = alphabet.size();
        analysis.symbolWidth = width;
        analysis.globalMetadataBytes = globalMetadataBytes;
        analysis.termThreshold = termThreshold;
        analysis.fullBlocks = fullBlocks;
        analysis.thresholdBlocks = thresholdBlocks;
        analysis.sharedBlocks = sharedBlocks;
        analysis.blockCount = blockCount;
        lastAnalysis = analysis;
        return output.toByteArray();
    }

    public static byte[] decode(byte[] container) {
        if (container.length < 6 || !Arrays.equals(Arrays.copyOf(container, 4), MAGIC)) {
            throw new IllegalArgumentException("invalid magic");
        }
        int[] offset = {4};
        if ((container[offset[0]++] & 0xff) != VERSION) {
            throw new IllegalArgumentException("invalid version");
        }
        int streamMode = container[offset[0]++] & 0xff;
        int originalLength = Math.toIntExact(readUvarint(container, offset));
        if (streamMode == MODE_RAW) {
            return Arrays.copyOfRange(container, offset[0], container.length);
        }
        int blockSize = Math.toIntExact(readUvarint(container, offset));
        List<BigInteger> fibs = fibonacciForBlockSize(blockSize);
        int blockCount = Math.toIntExact(readUvarint(container, offset));
        int alphabetSize = Math.toIntExact(readUvarint(container, offset));
        int width = container[offset[0]++] & 0xff;
        int[] alphabet = new int[alphabetSize];
        for (int i = 0; i < alphabetSize; i++) {
            alphabet[i] = Math.toIntExact(readUvarint(container, offset));
        }
        ByteArrayOutputStream output = new ByteArrayOutputStream(originalLength);
        for (int block = 0; block < blockCount; block++) {
            int mode = container[offset[0]++] & 0xff;
            int blockLength = Math.toIntExact(readUvarint(container, offset));
            int payloadLength = Math.toIntExact(readUvarint(container, offset));
            if (mode == MODE_RAW) {
                output.write(container, offset[0], payloadLength);
                offset[0] += payloadLength;
                continue;
            }
            int payloadEnd = offset[0] + payloadLength;
            int count = Math.toIntExact(readUvarint(container, offset));
            int packedLength = Math.toIntExact(readUvarint(container, offset));
            int[] symbols = unpack(container, offset[0], packedLength, count, width);
            offset[0] += packedLength;
            if (offset[0] != payloadEnd) {
                throw new IllegalArgumentException("invalid payload length");
            }
            int[] indices = new int[count];
            if (count > 0) {
                indices[count - 1] = alphabet[symbols[count - 1]];
                for (int i = count - 2; i >= 0; i--) {
                    indices[i] = alphabet[symbols[i]] + indices[i + 1];
                }
            }
            BigInteger value = BigInteger.ZERO;
            for (int index : indices) {
                value = value.add(fibs.get(index));
            }
            byte[] decodedBlock = unsignedBytes(value, blockLength);
            output.write(decodedBlock, 0, decodedBlock.length);
        }
        byte[] decoded = output.toByteArray();
        if (decoded.length != originalLength || blockSize <= 0) {
            throw new IllegalArgumentException("invalid decoded length");
        }
        return decoded;
    }

    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            throw new IllegalArgumentException("usage: FisaBenchmark <file> [block-size]");
        }
        Path path = Paths.get(args[0]);
        int blockSize = args.length >= 2 ? Integer.parseInt(args[1]) : 256;
        int warmups = args.length >= 3 ? Integer.parseInt(args[2]) : 1;
        byte[] source = Files.readAllBytes(path);
        for (int warmup = 0; warmup < warmups; warmup++) {
            byte[] encoded = encode(source, blockSize);
            if (!Arrays.equals(source, decode(encoded))) {
                throw new AssertionError("roundtrip failed");
            }
        }
        long start = System.nanoTime();
        byte[] encoded = encode(source, blockSize);
        long encodedAt = System.nanoTime();
        byte[] decoded = decode(encoded);
        long finished = System.nanoTime();
        if (!Arrays.equals(source, decoded)) {
            throw new AssertionError("roundtrip failed");
        }
        double encodeSeconds = (encodedAt - start) / 1e9;
        double decodeSeconds = (finished - encodedAt) / 1e9;
        Locale.setDefault(Locale.US);
        System.out.printf(
            "file,block_size,original_bytes,encoded_bytes,ratio,encode_seconds,decode_seconds,encode_mib_s,decode_mib_s,alphabet_size,symbol_width,global_metadata_bytes,k_star,full_blocks,k_star_blocks,k_star_fraction,shared_blocks,shared_block_fraction%n"
        );
        System.out.printf(
            "%s,%d,%d,%d,%.9f,%.6f,%.6f,%.6f,%.6f,%d,%d,%d,%d,%d,%d,%.9f,%d,%.9f%n",
            path.getFileName(), blockSize, source.length, encoded.length,
            (double) encoded.length / source.length, encodeSeconds, decodeSeconds,
            source.length / 1048576.0 / encodeSeconds,
            source.length / 1048576.0 / decodeSeconds,
            lastAnalysis.alphabetSize,
            lastAnalysis.symbolWidth,
            lastAnalysis.globalMetadataBytes,
            lastAnalysis.termThreshold,
            lastAnalysis.fullBlocks,
            lastAnalysis.thresholdBlocks,
            lastAnalysis.fullBlocks == 0 ? 0.0
                : (double) lastAnalysis.thresholdBlocks / lastAnalysis.fullBlocks,
            lastAnalysis.sharedBlocks,
            lastAnalysis.blockCount == 0 ? 0.0
                : (double) lastAnalysis.sharedBlocks / lastAnalysis.blockCount
        );
    }
}
