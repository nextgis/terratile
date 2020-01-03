#include "zlib.h"

#include "TemporaryOutputStream.hpp"

uint32_t
TemporaryOutputStream::write(const void *ptr, uint32_t size)
{
    ss.write((const char*) ptr, size);
    return size;
}

std::string TemporaryOutputStream::compress()
{
    z_stream zs;

    zs.zalloc = Z_NULL;
    zs.zfree = Z_NULL;
    zs.opaque = Z_NULL;
    zs.avail_in = 0;
    zs.next_in = Z_NULL;

    constexpr int window_bits = 15 + 16; // gzip with windowbits of 15
    constexpr int mem_level = 8;

    if (deflateInit2(&zs, Z_DEFAULT_COMPRESSION, Z_DEFLATED, window_bits, mem_level, Z_DEFAULT_STRATEGY) != Z_OK)
        throw(std::runtime_error("deflateInit failed while compressing!"));

    std::string str = ss.str();
    zs.next_in = (Bytef*)str.data();
    zs.avail_in = str.size();

    int ret;
    char outbuffer[32768];
    std::string outstring;

    do {
        zs.next_out = reinterpret_cast<Bytef*>(outbuffer);
        zs.avail_out = sizeof(outbuffer);

        ret = deflate(&zs, Z_FINISH);

        if (outstring.size() < zs.total_out) {
            outstring.append(outbuffer, zs.total_out - outstring.size());
        }
    } while (ret == Z_OK);

    deflateEnd(&zs);

    if (ret != Z_STREAM_END) {
        throw(std::runtime_error("deflate failed while compressing!"));
    }

    return outstring;

}
