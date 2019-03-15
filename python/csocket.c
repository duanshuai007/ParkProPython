#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>

int main(int argc, char *argv[])
{
    int socket_fd;
    struct sockaddr_in server_addr;
    //char buf[] = "hello python!";
    char buf[] = "Message:Charge:LA12345N:12";
    
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(9876);

    socket_fd = socket(PF_INET, SOCK_STREAM, 0);
    if (socket_fd < 0)
    {
        perror("socket");
        return -1;
    }

    if (connect(socket_fd, (struct sockaddr *)&server_addr, sizeof(struct sockaddr)) < 0) 
    {
        perror("connect");
        return -1;
    }

    printf("connected to server/n");



    while(1)
    {
        send(socket_fd, buf, strlen(buf), 0);
        sleep(2);
    }

    return 0;
}

