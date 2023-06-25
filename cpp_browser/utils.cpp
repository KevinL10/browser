#include <algorithm>
#include <cctype>
#include <iostream>
#include <string>
// https://stackoverflow.com/questions/9358718/similar-function-in-c-to-pythons-strip
template <std::ctype_base::mask mask>
class IsNot {
    std::locale myLocale;  // To ensure lifetime of facet...
    std::ctype<char> const* myCType;

   public:
    IsNot(std::locale const& l = std::locale())
        : myLocale(l), myCType(&std::use_facet<std::ctype<char> >(l)) {}
    bool operator()(char ch) const { return !myCType->is(mask, ch); }
};

typedef IsNot<std::ctype_base::space> IsNotSpace;

std::string trim(std::string const& original) {
    std::string::const_iterator right =
        std::find_if(original.rbegin(), original.rend(), IsNotSpace()).base();
    std::string::const_iterator left =
        std::find_if(original.begin(), right, IsNotSpace());
    return std::string(left, right);
}

void replaceAll(std::string& subject, const std::string& search,
                const std::string& replace) {
    size_t pos = 0;
    while ((pos = subject.find(search, pos)) != std::string::npos) {
        subject.replace(pos, search.length(), replace);
        pos += replace.length();
    }
}

std::string lower(const std::string& str) {
    std::string result;
    result.reserve(str.size());

    for (char c : str) {
        result.push_back(std::tolower(c));
    }

    return result;
}