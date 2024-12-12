#!/usr/bin/env python3

import argparse
from collections import Counter
from itertools import chain

parser = argparse.ArgumentParser(
    description = """
        Program to parse file with tcpdump or icmp ping output \n.
        You must define '-n' variable.
    """
)
parser.add_argument("file", help="file with icmp ping or tcpdump with icmp packets output")
parser.add_argument("-n", "--number", type=int, required=True, help="define how many string 'seq' or 'icmp_seq=' must be same")
parser.add_argument("-mode", "--mode", type=str, choices=["ping", "tcpdump"], default="tcpdump", help="parse 'tcpdump' or 'linux ping' log file")


if __name__ == "__main__":
    args = parser.parse_args()

    all_lines = chain(open(args.file))

    if args.mode == "tcpdump":
        print('mode je nastaveno na tcpdump:')
        print("")
        icmp = dict()
        for line in all_lines:
            line = line.strip()                           # remove all leading and trailing characters removed - default remove whitespace
            if 'ICMP echo' in line:                       # find 'ICMP echo' string in e.g: 11:11:04.398236 IP 82.99.137.41 > 192.168.0.169: ICMP echo reply, id 39411, seq 193, length 64
                listFromLine = line.split(", ")           # split line by ", " char. e.g. line is: 11:11:04.357423 IP 192.168.0.169 > 82.99.137.41: ICMP echo request, id 39411, seq 189, length 64
                id = listFromLine[-3].split()[1]          # get third last item from list and return string e.g: 'id 39411', split string by space and return list, and from list get second item
                seq = listFromLine[-2].split()[1]
                if id in icmp:
                    temp_list = icmp[id]
                    temp_list.append(int(seq))
                    icmp[id] = temp_list
                else:
                    icmp = {id: []}
        # sort my icmp dict, where key is 'id' and item is list of sequense numbers e.g: {'22637': ['1', '2', '2', '3', '3', '4', '4']}
        for key in icmp:
            tmp_list = icmp[key]
            tmp_list = sorted(tmp_list)
            icmp[key] = tmp_list
        # we have a icmp dict with sorted sequence numbers
        for key in icmp:
            sorted_list = icmp[key]       # get sorted_list from key=id 
            first_seq = sorted_list[0]    # get first item from sorted_list, e.g. 1 or 29
            last_seq = sorted_list[-1]    # get last item from sorted_list, e.g. 120 or 180

            # check if sequence numbers exists one by one in sorted_list. e.g if sequence 3 is in sorted_list = [1, 2, 4]
            print('Check if sequence numbers exists one by one:')
            temp_set = set(sorted_list)
            result_bool = True
            for n in range(first_seq, last_seq + 1):
                if n not in temp_set:
                    print(f"error: missing sequence number {n} in ICMP echo id: {key}")
                    result_bool = False
            if result_bool:
                print("--PASS")

            # check if exists n exactly same sequence number in sorted_list
            print("")
            print(f"Check if exists exactly {args.number} sequence numbers in ICMP echo packets in file {args.file}")
            counter = Counter(sorted_list)        # counter = Counter([1, 2, 2, 3, 3, 4, 4]) return Counter({2: 2, 3: 2, 4: 2, 1: 1}) 
            for n in range(first_seq, last_seq + 1):
                if counter[n] == args.number:     # Counter object return a zero count for missing items: counter[10] return 0
                    pass
                else:
                    print(f"error: in ICMP echo id: {key} must be {args.number} sequences for every sequence, but id {key} has only {counter[n]} sequences for sequnce {n}")
