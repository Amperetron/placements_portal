#include <iostream>
using namespace std;

bool print_composite(int n){
    if (n<0){
        return false;
    }
    if (n==2){
        return false;
    }
    if (n%2==0){
        return true;
    }
     for (int i=3;i<n;i++){
        if (n%i==0){
            return true;
        }
    }
    return false;
}

int main()
{
    
    int n;
    cin>>n;
    
    for(int i=2; i <= n; i++){
        if(print_composite(i))
            cout<<i<<"is composite"<<endl;
    }
    cout<<n<<"isnt composite"<<endl;
    return 0;
}

// #TODO: fix the composite logic in the lines 27 to 33