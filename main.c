#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <pthread.h>

#include "message.h"
#include "LPRCClientSDK.h"

#define CAMERA_PORT 8080

char *pstrCameraIN_ip = (char *)"192.168.200.251";
char *pstrCameraOUT_ip = (char *)"192.168.200.252";

#define USE_QUEUE

#ifdef USE_QUEUE
#include "msgqueue.h"
static int siMsgID = 0;
#else
static volatile int send_en = 0;
static char g_SocketSendBuff[128];
#endif

#if 1
#define OPENDOOR(ip,port)  CLIENT_LPRC_SetRelayClose((ip), port)
#define CLOSEDOOR(ip,port) CLIENT_LPRC_DropRod((ip), port)
#else
#define OPENDOOR()
#define CLOSEDOOR()
#endif

static void get_cur_time(char *timebuff)
{
    time_t sec;
    struct tm *tm;
    sec = time(NULL);
    tm = localtime(&sec);

    sprintf(timebuff, "%d-%02d-%02d %02d:%02d:%02d", tm->tm_year + 1900, tm->tm_mon + 1,
            tm->tm_mday, tm->tm_hour, tm->tm_min, tm->tm_sec);
}

void LPRC_DataEx2CallBackHandler(CLIENT_LPRC_PLATE_RESULTEX *recResult, LDWORD dwUser)
{
    char timebuff[20] = {0};
    char CarINorOUT[4] = {0};
    char sendbuffer[128] = {0};

    if (strcmp(recResult->chCLIENTIP, pstrCameraIN_ip) == 0) {
        //有车进入停车场
        if (recResult->pPlateImage.nLen > 0) {

            printf("\n门口%s: 车牌号码：%s:%s\n", \
                    recResult->chCLIENTIP, \
                    recResult->chColor, \
                    recResult->chLicense);

            strcpy(CarINorOUT, MESSAGE_CAR_IN);

            goto OK;
        }
    } else if (strcmp(recResult->chCLIENTIP, pstrCameraOUT_ip) == 0) {
        //有车离开停车场
        if (recResult->pPlateImage.nLen > 0) {

            printf("\n桌子%s: 车牌号码：%s:%s\n",\
                    recResult->chCLIENTIP,\
                    recResult->chColor,\
                    recResult->chLicense);

            strcpy(CarINorOUT, MESSAGE_CAR_OUT);

            goto OK;
        }
    }

    return;

OK:
    sprintf(timebuff, "%04d-%02d-%02d %02d:%02d:%02d", recResult->shootTime.Year, recResult->shootTime.Month, recResult->shootTime.Day,
            recResult->shootTime.Hour, recResult->shootTime.Minute, recResult->shootTime.Second);
    sprintf(sendbuffer, "%s,%s,%s,%s,%s", MESSAGE_HEAD, CarINorOUT, recResult->chColor, recResult->chLicense, timebuff);
#ifdef USE_QUEUE
    sendMsgQueue(siMsgID, CLIENT_TYPE, (char *)&sendbuffer, sizeof(sendbuffer));
#else
    memset(&g_SocketSendBuff, 0, sizeof(g_SocketSendBuff));
    strncpy(g_SocketSendBuff, sendbuffer, strlen(sendbuffer));
    send_en = 1;
#endif
}

// 输出连接状态的回调函数
void ConnectStatus(char *chCLIENTIP, UINT Status, LDWORD dwUser)
{
    if(strcmp(chCLIENTIP, pstrCameraIN_ip) == 0)
    {
        if(Status == 0)
        {
            printf("%s connect fail!\n", chCLIENTIP);
        } else {
            //printf("%s connect Normal!\n", chCLIENTIP);
        }
    }
}

void AlarmCallBackHandler(CLIENT_LPRC_DEVDATA_INFO *alarmInfo, LDWORD dwUser)
{
    printf("alarm callback\r\n");
}

//专门用于处理抬杆动作
static void pthread_doorlockctl_handler(void *arg)
{
    char recvbuff[128];
    char *string;
    //int fd = *((int *)arg);
    int ret;
    fd_set read_fds;
    //fd_set write_fds;
    struct timeval tv;
    int fd = *((int *)arg);

    while(1)
    {
        tv.tv_sec = 5;
        tv.tv_usec = 0;
        FD_ZERO(&read_fds);
        FD_SET(fd, &read_fds);
        //FD_SET(fd, &write_fds);
        memset(recvbuff, 0, sizeof(recvbuff));

        //ret = select(fd+1, &read_fds, &write_fds, NULL, NULL);
        ret = select(fd + 1, &read_fds, NULL, NULL, &tv);
        if (ret == 0) {
            //timeout
        } else if (ret == -1) {
            //failed
        } else {
            //success
            if (FD_ISSET(fd, &read_fds)) {
                FD_CLR(fd, &read_fds);
                //printf("socket readable\r\n");
                ret = recv(fd, recvbuff, sizeof(recvbuff), 0);
                if(ret < 0) {
                    continue;
                } else if (ret == 0) {
                    continue;
                }

                printf("C Socket Recv:%s\r\n", recvbuff);

                string = strstr(recvbuff, MESSAGE_HEAD);
                if ( string ) {
                    if ( strstr(string, MESSAGE_CMD_OPENDOOR) ) {
                        if ( strstr( string, MESSAGE_DEVICE_IN) ) {
                            OPENDOOR( pstrCameraIN_ip, CAMERA_PORT);
                        } else if ( strstr( string, MESSAGE_DEVICE_OUT)) {
                            OPENDOOR( pstrCameraOUT_ip, CAMERA_PORT);
                        }
                    } else if ( strstr( string, MESSAGE_CMD_CLOSEDOOR)) {
                        if ( strstr( string, MESSAGE_DEVICE_IN)) {
                            CLOSEDOOR( pstrCameraIN_ip, CAMERA_PORT);
                        } else if ( strstr( string, MESSAGE_DEVICE_OUT)) {
                            CLOSEDOOR( pstrCameraOUT_ip, CAMERA_PORT);
                        }
                    }
                }
            } 
        }
    }
}

void GPIOCallBackHandler(char *chWTYIP, CLIENT_LPRC_GPIO_In_Statue *pGpioState)
{
    char CAROK[10] = {0};
#ifdef USE_QUEUE
    char sendbuffer[128] = {0};
    char timebuff[20] = {0};
#endif

    if (strcmp(chWTYIP, pstrCameraIN_ip) == 0) {
        //gpio0
        if (pGpioState->gpio_in0) {
            strcpy(CAROK, MESSAGE_CAR_IN_OK);
            goto DO_SEND;
        } else {

        }
    }else if (strcmp(chWTYIP, pstrCameraOUT_ip) == 0) {
        //gpio0
        if (pGpioState->gpio_in0) {
            strcpy(CAROK, MESSAGE_CAR_OUT_OK);
            goto DO_SEND;
        } else {

        }  
    }

    return;

DO_SEND:
    get_cur_time(timebuff);
    sprintf(sendbuffer, "%s,%s,%s", MESSAGE_HEAD, CAROK, timebuff);
#ifdef USE_QUEUE
    sendMsgQueue(siMsgID, CLIENT_TYPE, (char *)&sendbuffer, sizeof(sendbuffer));
#else
    memset(&g_SocketSendBuff, 0, sizeof(g_SocketSendBuff));
    strncpy(g_SocketSendBuff, sendbuffer, strlen(sendbuffer));
    send_en = 1;
#endif
}

int main(int argc, char **argv)
{
    int     ret;
    char    *chPath = (char *)"/home/frog/ParkProject/picture";
    pthread_t pthread_doorctl_id;

#if 1
    int server_fd;
    struct sockaddr_in server_addr;
    char recvbuff[128];
    int len;

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    //server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
    server_addr.sin_port = htons(9876);

    server_fd = socket(PF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return -1;
    }
#endif

#ifdef USE_QUEUE
    siMsgID = createMsgQueue(MSG_KEYFILE);
    if (siMsgID == -1) {
        printf("createMsgQueue failed\r\n");
        return -1;
    }
#endif

   // 注册获取识别结果数据的回调函数
    CLIENT_LPRC_RegDataEx2Event((CLIENT_LPRC_DataEx2Callback) LPRC_DataEx2CallBackHandler);
    // 注册链接状态的回调函数
    CLIENT_LPRC_RegCLIENTConnEvent ((CLIENT_LPRC_ConnectCallback) ConnectStatus);
    // 设置图片保存的路径（设置路径后，接口库会自动将识别结果保存到指定目录下）
    CLIENT_LPRC_SetSavePath(chPath);
    //设置gpio回掉函数
    CLIENT_LPRC_RegWTYGetGpioState((CLIENT_LPRC_GetGpioStateCallback) GPIOCallBackHandler);

    // 初始化。（多个相机的话，需要调用多次这个接口,输入不同的IP地址）
    ret =  CLIENT_LPRC_InitSDK(CAMERA_PORT, NULL, 0, pstrCameraIN_ip, 1);
    if (ret == 1)
    {
        printf("%s InitSDK fail\n\tthen quit\r\n", pstrCameraIN_ip);
        CLIENT_LPRC_QuitSDK();
        return -1;
    } else {
        printf("%s InitSDK success\n", pstrCameraIN_ip);
    }
    //2号相机
    ret =  CLIENT_LPRC_InitSDK(CAMERA_PORT, NULL, 0, pstrCameraOUT_ip, 2);
    if (ret == 1)
    {
        printf("%s InitSDK fail\n\tthen quit\r\n", pstrCameraOUT_ip);
        CLIENT_LPRC_QuitSDK();
        return -1;
    } else {
        printf("%s InitSDK success\n", pstrCameraOUT_ip);
    }

    if (connect(server_fd, (struct sockaddr *)&server_addr, sizeof(struct sockaddr)) < 0) {
        //if (errno != EISCONN)
        //    continue;
        perror("connect");
        return -1;
    }

    if (pthread_create(&pthread_doorctl_id, NULL, (void *)(pthread_doorlockctl_handler), (void *)&server_fd) == -1) {
        perror("pthread_create");
        return -1;
    }

    while(1)
    {
        memset(recvbuff, 0, sizeof(recvbuff));
        recvMsgQueue(siMsgID, CLIENT_TYPE, recvbuff);
        printf("C Socket Send:%s\r\n", recvbuff);
        len = send(server_fd, recvbuff, strlen(recvbuff), 0);
        if (len == strlen(recvbuff)) {
            printf("Send OK\r\n");
        }
    }

    close(server_fd);
    // 释放资源
    CLIENT_LPRC_QuitSDK();
#ifdef USE_QUEUE
    destoryMsgQueue(siMsgID);
#endif

    return 0;
}

