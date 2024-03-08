from mcrcon import MCRcon

try:
    with MCRcon("192.168.254.20", "1234", timeout=.1) as mcr: #send the whitelist command to minecraft server
        resp = mcr.command("/say hello")
        print(resp)
except Exception as e:
    print(f'No worky\n{e}')
