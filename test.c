#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <string.h>
#include <time.h>

char plate[][30] = {"¡…A12345","¡…B34567", "∫⁄C98D56", "æ©A9DC34", "√…B94250", "À’E98562", "œÊA9276",
                    "…¬A93827", "…¬B987DF", "∏ C95821", "º™J12458", "¥®D98765"};

int main(int argc, char *argv[])
{

    int fd;
    int ret;
    struct sockaddr_in server_addr;
    //char buff[] = "Message,In,¿∂,À’EQ513M,2019-2-20 13:46:21";

    time_t seconds;
    struct tm *tm;

    int no, type;
    char timebuff[32] = {0};
    char typebuff[10] = {0};
    char buff[128] = {0};

    if (argc < 2) {
        printf("./test no type\r\n");
        return -1;
    }

    no = atoi(argv[1]);
    type = atoi(argv[2]);

    seconds = time(NULL);
    tm = localtime(&seconds);
    sprintf(timebuff, "%d-%02d-%02d %02d:%02d:%02d", tm->tm_year + 1900, tm->tm_mon + 1,
            tm->tm_mday, tm->tm_hour, tm->tm_min, tm->tm_sec);
    //printf("no=%d,type=%d,time=%s\r\n", no, type, timebuff);

    switch(type) {
        case 1:
            // ª»Î
            strcpy(typebuff, "In");
            break;
        case 2:
            // ª»Î»∑»œ
            strcpy(typebuff, "InOK");
            break;
        case 3:
            // ª≥ˆ
            strcpy(typebuff, "Out");
            break;
        case 4:
            // ª≥ˆ»∑»œ
            strcpy(typebuff, "OutOK");
            break;
    }

    sprintf(buff, "Message,%s,%s,%s,%s", typebuff, "¿∂", plate[no], timebuff);

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    //server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(9876);

    fd = socket(PF_INET, SOCK_STREAM, 0); 
    if (fd < 0) {
        perror("socket");
        return -1;
    }  

    ret = connect(fd, (struct sockaddr *)&server_addr, sizeof(struct sockaddr));
    //printf("ret=%d,errno=%d\r\n", ret, errno);
    if (ret < 0)
        return -1;

    //while(1) {
        printf("socket:%s\r\n", buff);
        send(fd, buff, strlen(buff), 0); 
    
    //    sleep(2);
    //}

    return 0;
}
