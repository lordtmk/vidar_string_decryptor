# Miscellanous malware scripts

## Simple VIDAR string decryptor

Automating XOR decryption to ease analysis in IDA Pro.
Contains some functions that can be exported in your own programs, and produce a file containing all decrypted strings to use for IOC collecting.

Huge thanks to https://github.com/ioncodes/idacode that helped me a lot to write and debug this.

## IcedID unpacker and C2 extractor

Simple Python script wrote for Z2A challenge
Automatically unpack malware and extract its C2 URL.
