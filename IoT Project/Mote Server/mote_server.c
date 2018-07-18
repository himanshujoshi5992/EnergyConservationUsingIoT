/*SERVER
Command for compilation : sudo gcc server.c -o server -l pthread $(mysql_config --cflags --libs)
*/


#include<stdio.h>
#include<string.h>
#include<unistd.h>
#include<pthread.h>
#include<sys/socket.h>
#include<arpa/inet.h>
#include<my_global.h>
#include<mysql.h>


MYSQL *con;
char dBServerDatabaseName[10] = "iotproject";
pthread_mutex_t mutexLock = PTHREAD_MUTEX_INITIALIZER;


void receiveMessage(int clientSocket)
{	
	char msgIn[100];
	char *pMsgIn;
	short msgInLen;
	const char *delimiter = "\t";	
	char query[300];
	unsigned short columnNo = 1;
	
	msgInLen = recv(clientSocket, msgIn, sizeof(msgIn), 0);												/*Receiving*/
		
	if(msgInLen < 0)											
	{	
		perror("Could not receive the Client Datagram! ");
		
		if(close(clientSocket) == -1)
		{
			perror("Could not destroy the Client Socket! ");
		}
		
		pthread_exit(NULL);
	}

	printf("Received the Client Datagram (%hd B) = \n", msgInLen);
	printf("%s\n", msgIn);
	pMsgIn = strtok(msgIn, delimiter);
	strcpy(query, "INSERT INTO wifimote (AmbientLight,BarometricPressure,Proximity,RelativeHumidity,Temperature,IP,Date,Time)values (");
		//printf("%s\n", query);
	
	while(pMsgIn != NULL)
	{
		//printf("%s\n", pMsgIn);
		strcat(query, pMsgIn);
		pMsgIn = strtok(NULL, delimiter);
		
		if(columnNo == 5)
			strcat(query, ", \"");
		else if(columnNo == 6)
			strcat(query, "\", ");
		else			
			strcat(query, ", ");
		
		columnNo++;
		//printf("%s\n", query);
	}
	
	strcat(query, "CURDATE(), CURTIME());");
         //printf("%s\n", query);	
	pthread_mutex_lock(&mutexLock);
	
	if(mysql_query(con, query))
	{
	  	fprintf(stderr, "Could not execute the query! %s\n", mysql_error(con));
  	}
	
	pthread_mutex_unlock(&mutexLock);
    printf("Stored in the %s database.\n", dBServerDatabaseName);
    
    if(close(clientSocket) == -1)
    {
    	perror("Could not destroy the Client Socket! ");
    	pthread_exit(NULL);
    }
    
    printf("Destroyed the Client Socket.\n");
    printf("------------------------------\n\n\n");
   	pthread_exit(NULL);
}


void main()
{
	int serverSocket, clientSocket;
	const unsigned char serverIP[15] = "192.168.100.230";	//192.168.0.1 127.0.0.1
	const unsigned int serverPort = 9999;
	struct sockaddr_in serverSocketAddress;	
	char dBServerName[10] = "localhost";
	char dBServerUserName[10] = "root";
	char dBServerUserPassword[10] = "IIITB@123.";
	pthread_t t; 
	
	serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);	//--------------------------------------------------------------------Creation
	
	if(serverSocket == -1)
	{
		perror("Could not create the Server Socket! ");
		exit(1);
	}
	
	printf("Created the Server Socket = %d\n\n", serverSocket);	
	serverSocketAddress.sin_addr.s_addr = inet_addr(serverIP);
	serverSocketAddress.sin_port = htons(serverPort);
	serverSocketAddress.sin_family = AF_INET;
	
	if(bind(serverSocket, (struct sockaddr*)&serverSocketAddress, sizeof(serverSocketAddress)))		//--------------------------------Binding
	{
		perror("Could not bind the Server Socket! ");
		exit(1);
	}
	
	printf("Bound the Server Socket.\n\n");
	con = NULL;
	con = mysql_init(NULL);
	
    if(!con) 
    {
	    fprintf(stderr, "Could not initialize the MySQL database server! %s\n", mysql_error(con));
	    exit(1);
    }

	printf("Initialized the MySQL database server.\n\n");
	
    if(!mysql_real_connect(con, dBServerName, dBServerUserName, dBServerUserPassword, dBServerDatabaseName, 0, NULL, 0)) 
    {
	    fprintf(stderr, "Could not connect to the MySQL database server! %s\n", mysql_error(con));
	    mysql_close(con);
		exit(1);
    }
    
    printf("Connected to the %s database..........\n\n", dBServerDatabaseName);
    
    if(listen(serverSocket, 1000))		//--------------------------------------------------------------------------------------------Listening
    {
    	perror("Could not listen to the Server Socket! ");
    	exit(1);
    }
    
	printf("Listening to the Server Socket..........\n\n");
	
	while(1)
	{
		clientSocket = accept(serverSocket, (struct sockaddr*)NULL, 0);		//----------------------------------------------------Accepting
		
		if(clientSocket == -1)
		{
			perror("Could not create the Client Socket! ");
			continue;
		}
		
		printf("------------------------------\n");
		printf("Created the Client Socket = %d\n", clientSocket);
		
		if(pthread_create(&t, NULL, receiveMessage, clientSocket))
		{		
			perror("Could not create the Client Thread! ");
			
			if(close(clientSocket) == -1)
			{
				perror("Could not destroy the Client Socket! ");
			}
			
			continue;
		}
		
		printf("Created the Client Thread.\n");
		
		if(pthread_detach(t))
		{
			printf("Could not detach the Client Thread.\n");
			
			if(close(clientSocket) == -1)
			{
				perror("Could not destroy the Client Socket! ");
			}
			
			if(pthread_cancel(t))
			{
				perror("Could not cancel the Client Thread! ");
			}
			
			continue;
		}
		
		printf("Detached the Client Thread.\n");
	}
	
	mysql_close(con);
	
	if(close(serverSocket) == -1)
	{
		perror("Could not destroy the Server Socket! ");
		exit(1);
	}
	
	printf("Destroyed the Server Socket = %d", serverSocket);
	pthread_exit(NULL);
}
