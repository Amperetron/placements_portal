#include <iostream>
#include <cmath>
using namespace std;

bool checkMember(int n){
    //10^4 max limit.
    if (n>10000 || n<0){
        return false;
    }
    int a=1;
    int b=0;
    int c;
    while (c<n) {
        c=a+b;
        b=a;
        a=c;
        if (a==n){
            return true;
        }
    }
    return false;
}
int main (){
    int i;
    cin >> i;
    if (checkMember(i)){
        cout<< "yes "<<i<<" is a fibonacci number"<<endl;
        return 0;
    }
    cout<<"nope note a fibonacci number...";
    return 0;

}