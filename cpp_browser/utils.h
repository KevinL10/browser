#ifndef UTILS_H
#define UTILS_H
#include <cctype>
#include <string>

std::string trim(std::string const& original);

void replaceAll(std::string& subject, const std::string& search,
                const std::string& replace);

std::string lower(const std::string& str);
#endif
