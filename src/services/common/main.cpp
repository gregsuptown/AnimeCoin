#include <iostream>

enum MyColors {
    Red, white, Black_dqwdqw
};

int main() {
    MyColors c = MyColors::white;
    std::cout << MyColors::Red << std::endl;
    std::cout << std::string(MyColors::Red) << std::endl;
    std::cout << c << std::endl;
    return 0;
}