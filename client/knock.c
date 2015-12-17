/*
 * Copyright (c) 2012, Red Canari, Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *  * Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *  * Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *  * Neither the name of the <organization> nor the
 *    names of its contributors may be used to endorse or promote products
 *    derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */



#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

extern FILE *stderr;

#define KNOCK		"OOBRE_KNOCK"

#ifndef uint8_t
# define uint8_t unsigned char
#endif

#ifndef RTLD_NEXT
# define RTLD_NEXT      ((void *) -1l)
#endif

static ssize_t (*orig_send)(int, const void *, size_t, int) = NULL;
static size_t (*orig_fwrite)(const void *, size_t, size_t, FILE *) = NULL;
static ssize_t (*orig_write)(int, const void *, size_t) = NULL;
static ssize_t (*orig_sendto)(int, const void *, size_t, int, const struct sockaddr *, socklen_t) = NULL;
static unsigned int sent_hello = 0;
static uint8_t *knock_buf = NULL;
static int knock_len = -1;


#define NOTIFY_KNOCK(x)    fprintf(stderr, x "()'ing knocking sequence.\n")

static uint8_t
nibbleFromChar(char c)
{
	if(c >= '0' && c <= '9') return c - '0';
	if(c >= 'a' && c <= 'f') return c - 'a' + 10;
	if(c >= 'A' && c <= 'F') return c - 'A' + 10;
	return 255;
}

uint8_t *hexStringToBytes(char *inhex)
{
	uint8_t *retval;
	uint8_t *p;
	int len, i;
	
	len = strlen(inhex) / 2;
	retval = malloc(len+1);
	for(i=0, p = (uint8_t *) inhex; i<len; i++) {
		retval[i] = (nibbleFromChar(*p) << 4) | nibbleFromChar(*(p+1));
		p += 2;
	}
	retval[len] = 0;
	return retval;
}

uint8_t *get_knock(int *length) {
	char *knock_hex = getenv(KNOCK);
	if (knock_hex == NULL)
		return NULL;
        *length = strlen(knock_hex)/2;
	return hexStringToBytes(knock_hex);
}

ssize_t send(int sockfd, const void * buf, size_t len, int flags)
{
	if (sent_hello == 0) {
	    NOTIFY_KNOCK("send");
		orig_send(sockfd, knock_buf, knock_len, flags);
                sent_hello = 1;
	}
	return orig_send(sockfd, buf, len, flags);
}

size_t fwrite(const void *ptr, size_t size, size_t nitems, FILE *stream)
{
	struct stat statbuf;
	fstat(fileno(stream), &statbuf);

	if (sent_hello == 0 && S_ISSOCK(statbuf.st_mode)) {
		NOTIFY_KNOCK("fwrite");
		orig_fwrite(knock_buf, 1, knock_len, stream);
                sent_hello = 1;
	}
	return orig_fwrite(ptr, size, nitems, stream);
}

ssize_t write(int fildes, const void *buf, size_t nbyte) {
	struct stat statbuf;
	fstat(fildes, &statbuf);

	if (sent_hello == 0 && S_ISSOCK(statbuf.st_mode)) {
		NOTIFY_KNOCK("write");
		orig_write(fildes, knock_buf, knock_len);
		sent_hello = 1;
	}
	return orig_write(fildes, buf, nbyte);
}

ssize_t sendto(int socket, const void *buffer, size_t length, int flags, const struct sockaddr *dest_addr, socklen_t dest_len) {

	if (sent_hello == 0) {
		NOTIFY_KNOCK("sendto");
		orig_sendto(socket, knock_buf, knock_len, flags, dest_addr, dest_len);
		sent_hello = 1;
	}
	return orig_sendto(socket, buffer, length, flags, dest_addr, dest_len);
}

void __attribute__ ((constructor)) hijack_init(void)
{
	knock_buf = get_knock(&knock_len);
	if (knock_buf == NULL) {
		printf("Please set %s to a valid hex string.\n", KNOCK);
		exit(-1);
	}
	printf("Hooking all socket send/write functions.\n");
	orig_send = (ssize_t (*)(int, const void *, size_t, int))dlsym(RTLD_NEXT, "send");
	orig_fwrite = (size_t (*)(const void *, size_t, size_t, FILE *))dlsym(RTLD_NEXT, "fwrite");
	orig_write = (ssize_t (*)(int, const void *, size_t))dlsym(RTLD_NEXT, "write");
	orig_sendto = (ssize_t (*)(int, const void *, size_t, int, const struct sockaddr *, socklen_t))dlsym(RTLD_NEXT, "sendto");
}

