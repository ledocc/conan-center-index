#include <systemd/sd-daemon.h>

#include <iostream>



int main()
{
    int systemd_booted = sd_booted();
    
    if ( systemd_booted > 0 )  { std::cout << "This system is booted with systemd."; }
    if ( systemd_booted == 0 ) { std::cout << "This system is not booted with systemd."; }
    if ( systemd_booted < 0 ) { std::cout << "Error when call sd_booted function."; }
      
    return 0;
}
