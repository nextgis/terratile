#ifndef TEMPORARYOUTPUTSTREAM_HPP
#define TEMPORARYOUTPUTSTREAM_HPP

#include <sstream>

#include "ctb/CTBOutputStream.hpp"

class TemporaryOutputStream:
    public ctb::CTBOutputStream
{
public:
    TemporaryOutputStream() {}
    virtual uint32_t write(const void *ptr, uint32_t size);
    std::string compress();

private:
    std::stringstream ss;
};

#endif // TEMPORARYOUTPUTSTREAM_HPP
