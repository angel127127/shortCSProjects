import socket
import threading
import csv
import argparse

def getBanner(ip, port, addType):
    ## fetch banner for extra info on port
    try:
        s = socket.socket(addType, socket.SOCK_STREAM)
        s.settimeout(1)
        if addType == socket.AF_INET6:
            s.connect((ip,port,0,0))
        else:
            s.connect((ip,port))
        ## decodes bytes returned from s to a string
        banner=s.recv(1024).decode(errors="ignore").strip()
        if banner:
            return banner
        else:
            return "No banner"
    except:
        return "No banner"
    finally:
        s.close()


def scan(ip, port, resultsList, addType):
    ## scan port to confirm if it is open or closed, trying to add banner if open
    ## before saving the results to a list
    try:
        ## create socket object using ipv6 addresses and TCP
        s=socket.socket(addType, socket.SOCK_STREAM)
        s.settimeout(1)
        ## connects to socket depending on address type
        if addType == socket.AF_INET6:
            result = s.connect_ex((ip, port,0,0))
        else:
            result = s.connect_ex((ip, port))

        if result == 0: ## only open ports are printed to console
            banner = getBanner(ip, port, addType)
            print("*** Port", port, "open with banner:", banner)
            resultsList.append({"port": port, "status": "open", "banner":banner})
        else: ##closed
            resultsList.append({"port": port, "status": "closed", "banner": ""})
    except:
        resultsList.append({"port": port, "status": "error", "banner": ""})
    finally:
        s.close()


def saveResults(resultsList):
    ## saves results to a csv file
    filename = "scan_results.csv"
    with open(filename, "w", newline="") as f:
        ## add headers then list of ports and status'
        writer = csv.DictWriter(f, fieldnames=["port", "status", "banner"])
        writer.writeheader()
        writer.writerows(resultsList)


def main():
    ## create arguement parser object
    parser = argparse.ArgumentParser(description="Port Scanner")
    ## add required arguments
    parser.add_argument("--target", required=True, help="Target IP")
    parser.add_argument("--ports", required=True, help="Port range")
    ## parse arguments
    args = parser.parse_args()

    if args.target and args.ports:
        target=args.target
        ports=args.ports
    else:
        ## if no arguments, hardcodes values
        target="scanme.nmap.org"
        ports="1-100"
    
    ## converts target into ip address and address type (ipv4 or ipv6)
    ##ip = socket.gethostbyname(args.target)
    addrInfo = socket.getaddrinfo(target, None)
    ip = addrInfo[0][4][0]
    addType = addrInfo[0][0]

    startPort, endPort = map(int, args.ports.split("-"))

    print(f"\nScanning {args.target} ({ip}) from ports {startPort}-{endPort}...\n")

    resultsList = []
    threads = []
    ## creates threads to scan each port and starts them
    for port in range(startPort, endPort + 1):
        current = threading.Thread(target=scan, args=(ip, port, resultsList, addType))
        threads.append(current)
        current.start()
    ## enusre all threads are done
    for current in threads:
        current.join()
    ## save results
    saveResults(resultsList)
    print("\nScan complete and saved")

main()
