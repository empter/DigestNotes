# https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
import binascii
import socket


def send_udp_message(message, address, port):
    """send_udp_message sends a message to UDP server

    message should be a hexadecimal encoded string
    """
    message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")


def format_hex(hex):
    """format_hex returns a pretty version of a hex string"""
    octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
    pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
    return "\n".join(pairs)

message = "AA AA 01 00 00 01 00 00 00 00 00 00 " \
"07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"

response = send_udp_message(message, "8.8.8.8", 53)
print(format_hex(response))

# More details can be found
# https://tools.ietf.org/pdf/rfc1035.pdf
'''
format of all DNS messages:
+---------------------+
|        Header       |
+---------------------+
|       Question      | the question for the name server
+---------------------+
|        Answer       | Resource Records (RRs) answering the question
+---------------------+
|      Authority      | RRs pointing toward an authority
+---------------------+
|      Additional     | RRs holding additional information
+---------------------+
A query only need Header and Question sections.
An answer will contain at least first three sections.

# Header
0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F    Example of a query header section:
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      ID                       | AA AA - Arbitrary 16 bit ID
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   | 01 00 - Query parameters
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    QDCOUNT                    | 00 01 - Number of questions
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ANCOUNT                    | 00 00 - Number of answers
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    NSCOUNT                    | 00 00 - Number of authority records
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ARCOUNT                    | 00 00 - Number of additional records
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
An answer header must have same ID, QDCOUNT. Maybe 0 NSCOUNT, ARCOUNT or even ANCOUNTself.
ID (16 bit): identifier of the query
QR (1 bit): a query (0) or a response (1)
Opcode (4 bit): 0000 standard query, 0001 inverse query, and more...
AA (1 bit): Authoritative Answer, only valid in responses
TC (1 bit): TrunCation, 0 is not truncated
RD (1 bit): Recursion Desired, 1 is desired
RA (1 bit): Recursion Available, 1 means recursion is available
Z (3 bit): Reserved for future use. Must be zero
RCODE (4 bit): Response code, 0000 is no error and more...
XXCOUNT (16 bit): unsignd integer specifying the number of XX

# Question
0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F    Example of a query question section:
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               | 07 65 78 61 6D 70 6C 65 - 'example' needs 7 bytes
/                     QNAME                     / 03 63 6F 6D - 'com' needs 3 bytes
/                                               / 00 - zero byte to end the QNAME
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     QTYPE                     | 00 01 - 1 for A record
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     QCLASS                    | 00 01 - 1 for IN (internet) class
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
QNAME: a domain name represented as a sequence of labels, where each label\
       consists of a length octet followed by that number of octets.
       the length octet <= 63, so must start with 00 in bits
       if this length octet start with 11 in bits, then is a pointer.
# pointer
0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 1  1|                OFFSET                   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
11 followed by 14 bits which is an unsigned interger counts the byte offset.
offset = bytes before the pointer, e.g., 12 means there are 12 bytes before pointer.

# Answer
0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               | C0 0C - NAME by compressed format
/                                               /
/                      NAME                     /
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TYPE                     | 00 01
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     CLASS                     | 00 01
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TTL                      | 00 00
|                                               | 18 4c
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                   RDLENGTH                    | 00 04 - RDATA length 4 bytes
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
/                     RDATA                     / 5D B8 - IP of A record
/                                               / D8 22
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
NAME: same as QNAME, usually in compressed format (use pointer)
TYPE = QTYPE
CLASS = QCLASS
TTL (32 bit): unsigned integer specifying the time to live for this Response
RDLENGTH (16 bit): unsigned integer that specifies the length in octets of the RDATA
RDATA: The data we’ve been looking for!

# IN-ADDR.ARPA domain (REVERSE DNS)
Generally, inverse query in Query parameters is not implemented,
we use IN-ADDR.ARPA domain instead, it is the same with standard query,
but QTYPE = 0C (12), and QNAME = reverse_ip.in-addr.arpa
Example: ip 10.0.2.3
23 32 - ID
01 00 - Query parameters
00 01 - Number of questions
00 00 -           answers
00 00 -           authority records
00 00 -           additional records
01 33 - 1 octet: 3
01 32 - 1 octet: 2
01 30 - 1 octet: 0
02 31 30 - 2 octets: 10
07 69 6e 2d 61 64 64 72 - 7 octets: in-addr
04 61 72 70 61 - 4 octets: arpa
00 - End
00 0c - TYPE PTR
00 01 - Class IN
'''
