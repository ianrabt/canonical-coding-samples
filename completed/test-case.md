# Test Case
## Scenario
Testing throughput on a 200Gb/s Ethernet device

## Testing Plan
iPerf / iPerf3 seems like a great utility for this kind of testing!  It's cross-platform, and readily available in all major Linux distro's default repositories.

### Hardware setup -- must be done manually
We require a verified Ethernet device, capable of receiving and sending at least 200Gb/s.  We'll call this device en0.  Install en0 into a test bench we'll call host0.  Also install en1, the Ethernet device we want to test the bandwidth of, into another test bench called host1.

For consumer grade ethernet cables, you'd need to use a crossover Ethernet cable to allow bidirectional communication without a router.  For +100Gb/s speeds, it appears multiple cables are used.  I assume similar crossover cabling is used to allow two devices to communicate without a router on such networks.

Connect en0 and en1 together using a crossover ethernet cable(s).

### Networking setup -- use a script to automate these steps
We will configure en0 and en1 so they can communicate and are assigned IP addresses.

I assume `/dev/en0` exists on host0 and `/dev/en1` exists on host1.  This can be verified by `ip link show` -- change the device name as necessary.

On host0:
1. `ip address add 10.0.0.10/24 dev en0`
1. `ip link set dev en0 up`
1. Verify a route for 10.0.0.0/24 now exists using `ip route`

Similarly, on host1:
1. `ip address add 10.0.0.20/24 dev en1`
1. `ip link set dev en1 up`
1. Verify a route for 10.0.0.0/24 now exists using `ip route`

Run: `ping 10.0.0.20` on host0 and `ping 10.0.0.10` and verify they can reach each other.

To use iperf3, we must open port 5201 (udp and tcp) on host0 (arbitrarily picked to be the server).  If using vanilla Ubuntu, run `ufw allow 5201` to configure the firewall.  This can also directly be modified using `iptables`, to work on more distros.

### Bandwidth test -- use the same script to automate these steps
On host0, run `iperf3 -s` and on host1, run `iperf3 -c 10.0.0.10` to test TCP bandwidth and `iperf3 -c 10.0.0.10 -u` to test UDP bandwidth.  The "Bandwidth" column will display test results -- verify 200Gb/s was achieved (the script can automate this check as well, by checking the maximum speed from every test).

### Teardown
On host0:
1. `ip address delete dev en0`
2. `ip link set dev en0 down`
3. Remove physical hardware after powering down the system.

On host1 (similarly):
1. `ip address delete dev en1`
2. `ip link set dev en1 down`
3. Remove physical hardware after powering down the system.

## Additional notes
It is possible to install `en0` and `en1` on the same test bench, instead of using two separate computers!  However, care must be taken with the routing to ensure `lo` won't be used by the kernel -- as it can identify the two IPs are assigned to two interfaces on the same host, and might not actually transmit any data using the physical interfaces!  I'm not actually sure what Linux would do in this scenario.  I'd need to test real hardware to see how to set something like that up.  However, it shouldn't be too difficult to use `ip route` to change the routing table, and check what would happen using, say, `route get 10.0.0.10` to see what device would be used -- and make sure that device is the physical Ethernet device.
