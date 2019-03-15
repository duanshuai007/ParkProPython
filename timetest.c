#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <time.h>



int main(int argc,char * argv[])
{
    time_t sec;
    struct tm *tm;

    sec = time(NULL);
    printf("time=%d\r\n", sec);
    tm =localtime(&sec);

    printf("%d-%d-%d %d:%d:%d\r\n", tm->tm_year, tm->tm_mon, tm->tm_mday, tm->tm_hour, tm->tm_min, tm->tm_sec);


    return 0;
}
