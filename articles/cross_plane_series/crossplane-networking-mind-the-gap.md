---
title: "Crossplane Networking: Mind the Gap Between Your Cloud Resources"
published: false
description: "Understanding Crossplane v2 networking through the lens of the London Underground"
tags: ["kubernetes", "crossplane", "networking", "devops"]
series: "Infrastructure-as-Code Adventures"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/crossplane-infrastructure-mind-the-gap.png"
organization: "the-software-s-journey"
---

*How Crossplane v2 manages your Azure network infrastructure like Transport for London manages the Tube—with varying degrees of success and frequent engineering works*

## Introduction

Ever stood on a cramped Northern Line platform at half eight on a Tuesday morning, squashed between a tourist with an oversized rucksack and someone’s suspiciously damp umbrella, whilst the tannoy cheerfully announces “minor delays due to a passenger incident at Bank”? Behind that quintessentially British chaos is actually a rather brilliant network of tracks, signals, tunnels, and security checkpoints that somehow gets millions of Londoners where they need to be (eventually).

Crossplane Networking in version 2 works remarkably similar to the Tube: you declare where your “passengers” (data packets) need to go, and Crossplane builds and manages the entire transit infrastructure—tracks, transfers, turnstiles, and those baffling “no entry” signs that appear without explanation. The beauty is, unlike actual Transport for London, Crossplane won’t suddenly close half your network for weekend engineering works without telling you first.

Let’s explore how Crossplane Networking transforms your Azure infrastructure into a world-class metro system—one that actually runs on time.

## The Underground Map: Your Network Topology

When you look at the iconic London Underground map, you see coloured lines connecting stations across the city. In Crossplane Networking, your Azure infrastructure has a similar topology—though hopefully with fewer “severe delays” and “signal failures at Edgware Road.”

### **Virtual Networks = The Entire Underground Network**

Your Azure Virtual Network (VNet) is like the entire London Underground network—a self-contained transit system with its own tracks, stations, and occasionally baffling route diversions. Much like how TfL insists the Circle Line is actually a “service” rather than a proper circle anymore, Azure insists VNets are “software-defined” which is a fancy way of saying “imaginary but incredibly important.”

```yaml
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetwork
metadata:
  name: london-underground-vnet
spec:
  forProvider:
    location: UK South  # Proper London, not that Northern upstart
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    addressSpace:
      - 10.0.0.0/16  # Plenty of room for expansion, unlike the actual Tube
    tags:
      Network: "Production"
      Status: "Good service" # Unlike the actual Northern Line
      Delays: "None" # Revolutionary concept for TfL
```

### **Subnets = Different Tube Lines**

Just as the Tube has the Circle Line (which isn’t circular), the Northern Line (which has somehow split into about seventeen different branches), and the Piccadilly Line (which takes 90 minutes to get to Heathrow because it stops at every hamlet between here and Windsor), your VNet has subnets—each serving different purposes and zones:

```yaml
# The Northern Line (Public Subnet - Direct street access)
# Because everyone loves surfacing at a random exit half a mile from where you wanted
apiVersion: network.azure.upbound.io/v1beta1
kind: Subnet
metadata:
  name: northern-line-public
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    virtualNetworkNameSelector:
      matchLabels:
        network: london-underground
    addressPrefix: 10.0.1.0/24
    tags:
      Line: "Northern - High Barnet Branch"
      Status: "Minor delays due to an earlier incident"
      Tourists: "Many, with large backpacks"

---
# The Central Line (Private Subnet - Application tier)
# Deep underground where it's inexplicably hot even in February
apiVersion: network.azure.upbound.io/v1beta1
kind: Subnet
metadata:
  name: central-line-private
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    virtualNetworkNameSelector:
      matchLabels:
        network: london-underground
    addressPrefix: 10.0.2.0/24
    tags:
      Line: "Central - The Oven Line"
      Temperature: "Absolutely sweltering"
      Status: "Severe delays - signal failure at Holborn (again)"

---
# The Victoria Line (Private Subnet - Database tier)
# The newest line, though 'new' is relative when it opened in 1968
apiVersion: network.azure.upbound.io/v1beta1
kind: Subnet
metadata:
  name: victoria-line-database
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    virtualNetworkNameSelector:
      matchLabels:
        network: london-underground
    addressPrefix: 10.0.3.0/24
    delegations:
      - name: database-delegation
        properties:
          serviceName: Microsoft.DBforPostgreSQL/flexibleServers
    tags:
      Line: "Victoria - Actually works most of the time"
      Status: "Good service (miracles do happen)"
      Sealed: "Tighter than a Londoner's smile on the morning commute"
```

**The Pattern:**

- **Northern Line (Public)**: Web servers with street-level access, where tourists ask you for directions despite you clearly wearing headphones
- **Central Line (Private)**: Application servers requiring transfers, perpetually delayed at Liverpool Street
- **Victoria Line (Deep Private)**: Databases buried so deep underground even the Piccadilly Line looks shallow, accessible only to those with proper credentials and a strong constitution

## Stations and Platforms: Your Services

Each station on the Tube represents a service in your infrastructure. Some are busy interchange stations where you’ll definitely get elbowed in the ribs at least twice (load balancers), others are quiet local stops where you wonder if anyone actually lives there (single instances).

```yaml
# King's Cross Station (Application Gateway - Major interchange and source of confusion)
# Where six different lines meet and somehow nobody knows which platform they need
apiVersion: network.azure.upbound.io/v1beta1
kind: ApplicationGateway
metadata:
  name: kings-cross-app-gateway
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    
    # SKU - Standard_v2 because we're not savages using Basic
    sku:
      - name: Standard_v2
        tier: Standard_v2
        capacity: 2  # Two platforms, still massive queues
    
    # Gateway IP - The actual station entrance
    gatewayIpConfigurations:
      - name: gateway-ip-config
        subnetIdSelector:
          matchLabels:
            subnet: northern-line-public
    
    # Frontend - Where passengers (requests) arrive
    frontendIpConfigurations:
      - name: frontend-ip
        publicIpAddressIdSelector:
          matchLabels:
            gateway: kings-cross
    
    # Frontend ports - The ticket barriers
    frontendPorts:
      - name: https-port
        port: 443
      - name: http-port
        port: 80  # For redirecting to HTTPS, like redirecting tourists to the correct platform
    
    # Backend pools - Where trains (traffic) actually go
    backendAddressPools:
      - name: web-tier-pool
    
    # HTTP settings - How we talk to the backend
    backendHttpSettingsCollection:
      - name: backend-settings
        port: 80
        protocol: Http
        cookieBasedAffinity: Disabled  # Unlike the Tube, we don't play favourites
        requestTimeout: 30  # Longer than the average Londoner's patience
    
    # Listeners - The station announcements (mostly lies about "good service")
    httpListeners:
      - name: https-listener
        frontendIpConfigurationName: frontend-ip
        frontendPortName: https-port
        protocol: Https
    
    # Routing rules - The signage (equally confusing)
    requestRoutingRules:
      - name: main-routing-rule
        ruleType: Basic
        httpListenerName: https-listener
        backendAddressPoolName: web-tier-pool
        backendHttpSettingsName: backend-settings
        priority: 100
    
    tags:
      Station: "Kings Cross St Pancreas" # Yes, they misspelled it
      Tourists: "Absolutely loads"
      Platform9¾: "Still fictional, sadly"
      EurostarConnection: "Makes you feel inadequate about our trains"
```

**Station Classifications:**

- **King’s Cross (App Gateway)**: Major interchange, perpetual construction, tourists everywhere taking photos
- **Mornington Crescent (Single VM)**: Quiet station, occasional passenger, mainly exists for the radio quiz
- **Oxford Circus (Traffic Manager)**: Complete bedlam at rush hour, four different lines crossing, good luck

## Turnstiles and Oyster Readers: Network Security Groups

Just as you can’t board a Tube train without tapping your Oyster card at the turnstile (or faffing about with Apple Pay whilst the queue behind you tuts disapprovingly), packets can’t enter your Azure resources without passing through Network Security Groups (NSGs). They’re the digital equivalent of that one gate that always seems to reject your perfectly valid card whilst the tourist behind you sails through with a paper ticket from 1987.

```yaml
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityGroup
metadata:
  name: northern-line-nsg
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    tags:
      Purpose: "Northern Line Access Control"
      Status: "Rejecting valid cards since 2003"
      Tutting: "Enabled"

---
# Inbound rules - Who gets to tap in
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityRule
metadata:
  name: allow-https-from-internet
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    networkSecurityGroupNameSelector:
      matchLabels:
        nsg: northern-line
    
    name: AllowHTTPSInbound
    priority: 100  # Lower number = higher priority, like being first in the queue
    direction: Inbound
    access: Allow
    protocol: Tcp
    sourcePortRange: "*"
    destinationPortRange: "443"
    sourceAddressPrefix: Internet  # The great unwashed masses from street level
    destinationAddressPrefix: VirtualNetwork
    description: "Allow HTTPS like allowing people with valid Oyster cards"

---
# The "staff only" entrance
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityRule
metadata:
  name: allow-ssh-from-bastion
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    networkSecurityGroupNameSelector:
      matchLabels:
        nsg: northern-line
    
    name: AllowSSHFromBastion
    priority: 110
    direction: Inbound
    access: Allow
    protocol: Tcp
    sourcePortRange: "*"
    destinationPortRange: "22"
    sourceAddressPrefix: 10.0.100.0/24  # The bastion subnet, staff only
    destinationAddressPrefix: "*"
    description: "Staff entrance - no tourists asking where Platform 9¾ is"

---
# The "absolutely not" rule
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityRule
metadata:
  name: deny-rdp-from-internet
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    networkSecurityGroupNameSelector:
      matchLabels:
        nsg: northern-line
    
    name: DenyRDPFromInternet
    priority: 4096  # Maximum priority, maximum denial
    direction: Inbound
    access: Deny
    protocol: Tcp
    sourcePortRange: "*"
    destinationPortRange: "3389"
    sourceAddressPrefix: Internet
    destinationAddressPrefix: "*"
    description: "Like those angry barriers that slam shut when you try to tailgate"
```

**Associate NSG with Subnet** (like installing turnstiles at the platform entrance):

```yaml
apiVersion: network.azure.upbound.io/v1beta1
kind: SubnetNetworkSecurityGroupAssociation
metadata:
  name: northern-line-nsg-association
spec:
  forProvider:
    subnetIdSelector:
      matchLabels:
        subnet: northern-line-public
    networkSecurityGroupIdSelector:
      matchLabels:
        nsg: northern-line
```

**Security Zones by Line:**

- **Northern Line (Public NSG)**: Open turnstiles accepting passengers from the street, occasional tourist confusion, frequent card readers breaking
- **Central Line (Semi-Private NSG)**: Only accepts transfers from Northern Line, mysteriously always hot
- **Victoria Line (Restricted NSG)**: Staff-only access with proper credentials, no tourists asking if this goes to “Lester Square”

## Transfer Stations: Route Tables

Transfer stations like Bank (where you’ll walk for approximately seventeen minutes underground between platforms) or King’s Cross (where the signs are more decorative than informative) allow passengers to switch between lines. Azure Route Tables serve the same purpose—directing traffic between subnets, though hopefully with slightly clearer signage than “Way Out →” pointing at a solid wall.

```yaml
# Bank Station Route Table (Major Transfer Point and Underground Labyrinth)
# Connecting the Northern, Central, Waterloo & City, and DLR lines
# Also connecting your sanity to the void
apiVersion: network.azure.upbound.io/v1beta1
kind: RouteTable
metadata:
  name: bank-station-routes
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    disableBgpRoutePropagation: false  # BGP = "Bank's Generally Perplexing" routing
    tags:
      Station: "Bank/Monument (they're the same but also different)"
      WalkingDistance: "Approximately infinity"
      Signs: "Technically present but unhelpful"
      LostTourists: "Countless"

---
# Route to Internet (Exit to street level at last)
apiVersion: network.azure.upbound.io/v1beta1
kind: Route
metadata:
  name: route-to-street-level
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    routeTableNameSelector:
      matchLabels:
        station: bank
    
    name: ToInternetViaGateway
    addressPrefix: 0.0.0.0/0  # All of the internet, which is slightly more than all of London
    nextHopType: Internet
    description: "Exit to daylight - follow signs saying 'Way Out' for 400 metres"

---
# Associate route table with subnet
apiVersion: network.azure.upbound.io/v1beta1
kind: SubnetRouteTableAssociation
metadata:
  name: northern-line-routes
spec:
  forProvider:
    subnetIdSelector:
      matchLabels:
        subnet: northern-line-public
    routeTableIdSelector:
      matchLabels:
        station: bank
```

**Transfer Patterns:**

```
Northern Line → Virtual Network Gateway = Direct exit to street level (if you can find it)
Central Line → NAT Gateway → Internet = Must transfer at designated station, queue accordingly
Victoria Line → No external access = Sealed deep tunnel, staff corridors only, no tourists
```

**Common Transfer Station Configurations:**

```yaml
# Oxford Circus Route Table (Complete Bedlam Configuration)
# Where four lines meet and somehow create total chaos
apiVersion: network.azure.upbound.io/v1beta1
kind: RouteTable
metadata:
  name: oxford-circus-madness
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    
    routes:
      # Route to private subnet via NVA (Network Virtual Appliance = Angry station guard)
      - name: ToPrivateViaNVA
        addressPrefix: 10.0.2.0/24
        nextHopType: VirtualAppliance
        nextHopInIpAddress: 10.0.10.4  # The firewall, standing there judging you
      
      # Route to internet via NAT
      - name: ToInternetViaNAT
        addressPrefix: 0.0.0.0/0
        nextHopType: VirtualAppliance
        nextHopInIpAddress: 10.0.50.4  # NAT Gateway IP
    
    tags:
      Status: "Perpetually rammed"
      Escalators: "At least one always broken"
      RegentStreet: "Too expensive"
```

## The Piccadilly Line to Heathrow: Virtual Network Gateway

The Piccadilly Line connects central London directly to Heathrow Airport—your gateway to the outside world, assuming you’re willing to spend 90 minutes stopping at literally every station between Leicester Square and Terminal 5. In Azure network terms, this is your Virtual Network Gateway (VPN Gateway variant), though mercifully it doesn’t make you sit through Hounslow West, Hounslow Central, and Hounslow East in succession.

```yaml
# First, we need a dedicated subnet for the gateway
# Because gateways are posh and require their own platform
apiVersion: network.azure.upbound.io/v1beta1
kind: Subnet
metadata:
  name: gateway-subnet
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    virtualNetworkNameSelector:
      matchLabels:
        network: london-underground
    addressPrefix: 10.0.255.0/27  # Small subnet, exclusive platform
    name: GatewaySubnet  # MUST be called this, Azure is very particular
    tags:
      Line: "Piccadilly Extension"
      Destination: "Heathrow T5 and your overdraft"
      JourneyTime: "An eternity"

---
# Public IP for the gateway - The actual Heathrow entrance
apiVersion: network.azure.upbound.io/v1beta1
kind: PublicIP
metadata:
  name: heathrow-gateway-ip
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    allocationMethod: Static  # Not going anywhere, unlike your luggage
    sku: Standard
    tags:
      Gateway: "Heathrow International"
      Duty-Free: "Overpriced"
      WiFi: "Surprisingly decent"

---
# The actual VPN Gateway - Your connection to the world
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetworkGateway
metadata:
  name: heathrow-vpn-gateway
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    
    type: Vpn  # Could also be ExpressRoute if you're feeling fancy
    vpnType: RouteBased  # Like the Tube but more predictable
    enableBgp: false  # We don't need Border Gateway Protocol complicating things
    
    sku: VpnGw1  # Basic tier, like the Piccadilly line
    generation: Generation1
    
    # IP configuration - Where trains arrive at Heathrow
    ipConfigurations:
      - name: vnetGatewayConfig
        privateIpAllocationMethod: Dynamic
        subnetIdSelector:
          matchLabels:
            subnet: gateway-subnet
        publicIpAddressIdSelector:
          matchLabels:
            gateway: heathrow
    
    tags:
      Gateway: "Heathrow VPN Gateway"
      Terminals: "Still fewer than Heathrow has"
      SecurityQueue: "Inexplicably long despite it being 3am"
```

**Only public subnets (Northern Line) get direct routes to Heathrow.** Private subnets must transfer through other stations, much like how nobody actually wants to go to Hounslow but here we are anyway.

**Alternative: ExpressRoute (Private Jet of Network Connectivity)**

```yaml
# For when you're too important for the Piccadilly Line
# ExpressRoute = Helicopter directly from your building to Heathrow
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetworkGateway
metadata:
  name: private-jet-gateway
spec:
  forProvider:
    location: UK South
    type: ExpressRoute  # No stopping at every station
    sku: Standard  # Still cheaper than an actual private jet
    tags:
      Class: "First"
      Champagne: "Complimentary"
      CommonPeople: "Not invited"
```

## The Replacement Bus Service: NAT Gateway

Not all Tube lines go directly to the airport. Sometimes there’s “severe disruption on the District Line” (translation: someone looked at the tracks funny) and you must take the dreaded **replacement bus service**. This is your Azure NAT Gateway—a designated transfer point for private subnet traffic heading to the internet, operated by drivers who definitely know where they’re going (they don’t) and buses that turn up “every 10 minutes” (they won’t).

```yaml
# Public IP for NAT Gateway - The bus depot
apiVersion: network.azure.upbound.io/v1beta1
kind: PublicIP
metadata:
  name: replacement-bus-service-ip
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    allocationMethod: Static
    sku: Standard
    zones:  # Available in zones 1, 2, and 3 (like Oyster pricing)
      - "1"
    tags:
      Service: "Replacement Bus"
      Reliability: "Questionable"
      Driver: "Probably lost"
      Google Maps: "Frantically checking"

---
# The actual NAT Gateway - Victoria Station Shuttle
apiVersion: network.azure.upbound.io/v1beta1
kind: NATGateway
metadata:
  name: victoria-station-shuttle
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    
    sku:
      - name: Standard
    
    # How many IP addresses (buses) we can use
    idleTimeoutInMinutes: 4  # Passenger timeout, like waiting for a bus in the rain
    zones:
      - "1"
    
    publicIpAddressIds:
      - selector:
          matchLabels:
            service: replacement-bus
    
    tags:
      Service: "Victoria Shuttle to Internet"
      Status: "Running late"
      Reason: "Earlier incident" # It's always an earlier incident
      WiFi: "Doesn't work"

---
# Associate NAT Gateway with private subnet
# This is like putting up signs saying "Trains cancelled, get on this bus instead"
apiVersion: network.azure.upbound.io/v1beta1
kind: SubnetNatGatewayAssociation
metadata:
  name: central-line-to-nat
spec:
  forProvider:
    subnetIdSelector:
      matchLabels:
        subnet: central-line-private
    natGatewayIdSelector:
      matchLabels:
        service: victoria-shuttle
```

**The Journey from Private Subnet to Internet:**

```
Private subnet (Central Line - train broken down)
  ↓
"Please listen for announcements" (nobody understands them)
  ↓
NAT Gateway (Victoria Replacement Bus Service)
  ↓
Public IP (Bus eventually arrives, maybe)
  ↓
Virtual Network Gateway (Finally reach Heathrow)
  ↓
Internet (Freedom! Until the return journey...)
```

**Why Private Resources Can’t Go Directly:**
Just as you can’t take the Victoria Line to Heathrow (it doesn’t go there, despite what that confused tourist thinks), private subnet resources can’t go directly to the internet. They must:

1. Surface at a designated station (NAT Gateway)
1. Board the replacement bus service (NAT translation)
1. Share IP addresses with everyone else (like sardines on the bus)
1. Accept that this journey will take longer than expected
1. Wonder why they didn’t just walk

**NAT Gateway Features:**

- **Outbound only**: Like those exit-only barriers at stations that slam shut if you try to go backwards
- **Source NAT**: All your private VMs share the bus (public IP), contributing to traffic jams
- **Zonal redundancy**: Multiple buses in case one breaks down (likely)
- **Idle timeout**: If you faff about too long, connection drops like a phone call in a tunnel

## The Elizabeth Line Connection: VNet Peering

The new Elizabeth Line (Crossrail) connects previously separate networks—bringing together the wilds of Reading, the mysteries of Shenfield, and everything in between. After approximately 47 years of construction and only £4 billion over budget (a bargain by British infrastructure standards), it’s brilliant. In Azure, VNet Peering creates these cross-network connections, minus the parliamentary inquiries and scandals about tunneling under historic buildings.

```yaml
# Peering from London Underground to Crossrail Network
# East-West integration, just like the actual Elizabeth Line
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetworkPeering
metadata:
  name: elizabeth-line-eastbound
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    virtualNetworkNameSelector:
      matchLabels:
        network: london-underground
    
    # The remote network we're connecting to
    remoteVirtualNetworkId: /subscriptions/{subscription-id}/resourceGroups/crossrail/providers/Microsoft.Network/virtualNetworks/crossrail-vnet
    
    # Peering settings
    allowVirtualNetworkAccess: true  # Yes, trains can cross
    allowForwardedTraffic: true  # Traffic from other networks allowed through
    allowGatewayTransit: false  # We're not sharing our fancy gateway
    useRemoteGateways: false  # Not using their gateway either, thank you
    
    tags:
      Line: "Elizabeth Line Eastbound"
      Status: "Actually working (miraculously)"
      OpenedIn: "2022 (only 3 years late)"
      OriginalBudget: "A distant memory"

---
# Peering must be bidirectional, like trains going both ways
# This is the westbound connection
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetworkPeering
metadata:
  name: elizabeth-line-westbound
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: crossrail-project
    virtualNetworkNameSelector:
      matchLabels:
        network: crossrail-vnet
    
    # Peering back to original network
    remoteVirtualNetworkId: /subscriptions/{subscription-id}/resourceGroups/tfl/providers/Microsoft.Network/virtualNetworks/london-underground-vnet
    
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    allowGatewayTransit: false
    useRemoteGateways: false
    
    tags:
      Line: "Elizabeth Line Westbound"
      Reading: "Surprisingly far from London"
      Wifi: "Mostly works"
      ProjectOverruns: "Don't ask"
```

**VNet Peering vs VPN Gateway:**

|Feature |VNet Peering (Elizabeth Line)|VPN Gateway (Actual train to Reading)   |
|--------|-----------------------------|----------------------------------------|
|Speed   |Fast, direct connection      |Slower, encrypted tunnel                |
|Cost    |Cheaper                      |More expensive                          |
|Setup   |Quick                        |Takes ages (like the real Crossrail)    |
|Latency |Low                          |Higher                                  |
|Security|Private Azure backbone       |Encrypted over internet                 |
|Use case|Connect Azure VNets          |Connect to on-premises or dodgy networks|

**Use Cases for VNet Peering:**

- **Production ↔ Development**: So developers can break things without affecting production (hopefully)
- **Different regions**: London VNet ↔ Manchester VNet (North-South divide in infrastructure form)
- **Hub-and-Spoke**: Central hub VNet peers with multiple spoke VNets, like Victoria Line being the hub
- **Cross-subscription**: Different departments, same company (like different TfL subsidiaries nobody knew existed)

**Global VNet Peering** (International Elizabeth Line):

```yaml
# Connect London to New York network (the actual Special Relationship)
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetworkPeering
metadata:
  name: transatlantic-tunnel
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    virtualNetworkNameSelector:
      matchLabels:
        network: london-underground
    
    # Peering across regions (basically magic)
    remoteVirtualNetworkId: /subscriptions/{sub}/resourceGroups/mta/providers/Microsoft.Network/virtualNetworks/new-york-subway
    
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    
    tags:
      Connection: "The Dream of Victorian Engineers"
      Cost: "Eye-watering"
      Latency: "Actually quite good"
      TimeDifference: "5 hours, perpetually confusing"
```

## The DLR Private Railway: Azure Private Link

The Docklands Light Railway (DLR) is a separate, more exclusive system connecting specialized areas like Canary Wharf (where bankers live in their natural habitat). It’s automatic, slightly futuristic, and makes you feel like you’re in a science fiction film—until you remember you’re still in South Quay. Azure Private Link works similarly—creating private, high-security connections to Azure services without touching the public internet, perfect for when you’re too important to mingle with common HTTP traffic.

```yaml
# Private Endpoint - Your exclusive DLR station
# Connecting directly to Azure Storage without using public transport (internet)
apiVersion: network.azure.upbound.io/v1beta1
kind: PrivateEndpoint
metadata:
  name: dlr-to-storage-account
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    
    # Which subnet gets this exclusive service
    subnetIdSelector:
      matchLabels:
        subnet: victoria-line-database
    
    # Private connection to Azure Storage
    privateLinkServiceConnections:
      - name: storage-private-connection
        isManualConnection: false  # Automatic approval, VIP treatment
        privateLinkServiceId: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/canarywharf-storage
        groupIds:
          - blob  # Connecting to blob storage
        requestMessage: "DLR connection for executives only"
    
    tags:
      Service: "DLR to Canary Wharf Storage"
      Class: "Executive"
      PublicTransport: "Absolutely not"
      Views: "Docklands skyline, mostly cranes"

---
# Private DNS Zone - Making sure DLR stations have proper addresses
apiVersion: network.azure.upbound.io/v1beta1
kind: PrivateDnsZone
metadata:
  name: blob-storage-dns
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    name: privatelink.blob.core.windows.net  # Azure's DNS for blob storage
    tags:
      Purpose: "DLR Station Naming System"
      Clarity: "Better than actual TfL signage"

---
# Link DNS Zone to VNet
apiVersion: network.azure.upbound.io/v1beta1
kind: PrivateDnsZoneVirtualNetworkLink
metadata:
  name: link-dns-to-vnet
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    privateDnsZoneNameSelector:
      matchLabels:
        dns: blob-storage
    virtualNetworkIdSelector:
      matchLabels:
        network: london-underground
    registrationEnabled: false
    tags:
      Purpose: "Connect DLR naming to Underground network"
```

**Private Link to Azure SQL Database** (The Executive Shuttle):

```yaml
apiVersion: network.azure.upbound.io/v1beta1
kind: PrivateEndpoint
metadata:
  name: dlr-to-sql-database
spec:
  forProvider:
    location: UK South
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    
    subnetIdSelector:
      matchLabels:
        subnet: victoria-line-database
    
    privateLinkServiceConnections:
      - name: sql-private-connection
        isManualConnection: false
        privateLinkServiceId: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Sql/servers/canarywharf-sql
        groupIds:
          - sqlServer
        requestMessage: "Executive database access, no riff-raff"
    
    tags:
      Service: "DLR to SQL Database"
      Passengers: "Data packets in suits"
      OffPeak: "Never, always busy making money"
```

**Available Private Link Services** (Your DLR Network Destinations):

|Azure Service           |Group ID |Like Having DLR Access To…            |
|------------------------|---------|--------------------------------------|
|Storage Account (Blob)  |blob     |The document archive at Canary Wharf  |
|Storage Account (File)  |file     |The corporate shared drive            |
|Azure SQL Database      |sqlServer|The financial records vault           |
|Cosmos DB               |Sql      |The globally distributed ledger       |
|Key Vault               |vault    |The literal bank vault                |
|Azure Container Registry|registry |The approved Docker image library     |
|Event Hubs              |namespace|The trading floor message bus         |
|Service Bus             |namespace|The executive memo distribution system|

**Why Use Private Link Instead of Public Internet?**

**Regular Internet Connection (Getting the District Line to Canary Wharf):**

```
Your VM → Public IP → Internet → Public endpoint → Storage Account
  ↓
Slow, exposed to traffic, shares route with tourists
Goes through Zone 1 unnecessarily
Costs more (data egress charges like peak-time fares)
Security nightmare (anyone can see you travelling)
```

**Private Link (Taking the DLR):**

```
Your VM → Private Endpoint → Azure Backbone → Storage Account
  ↓
Fast, direct, no stopping at every station
Never touches public internet
Lower latency (direct route, no Oxford Circus transfers)
More secure (private railway, no randos)
Better for compliance (PCI-DSS, GDPR etc.)
```

**Service Endpoint vs Private Endpoint:**

|Feature      |Service Endpoint (Reserved Carriage)       |Private Endpoint (Actual DLR)                            |
|-------------|-------------------------------------------|---------------------------------------------------------|
|IP Address   |Service keeps public IP                    |Service gets private IP in your VNet                     |
|Traffic Route|Via Azure backbone but service still public|Fully private, service only in your network              |
|Security     |Source IP filtering                        |Full network isolation                                   |
|Cost         |Free                                       |Pay per endpoint (£5-8/month, less than an Oyster top-up)|
|Use Case     |Budget-conscious, still want Azure backbone|Maximum security, compliance requirements                |

**Setting up Private Link Correctly:**

```yaml
# Step 1: Create the Private Endpoint (DLR Station in your subnet)
# Step 2: Create Private DNS Zone (Station names)
# Step 3: Link DNS Zone to VNet (Publish station names)
# Step 4: Create DNS A Record (Actual address mapping)

apiVersion: network.azure.upbound.io/v1beta1
kind: PrivateDnsARecord
metadata:
  name: storage-account-record
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    zoneName: privatelink.blob.core.windows.net
    ttl: 3600  # How long to remember the station location
    records:
      - 10.0.3.4  # The private IP of the endpoint
    tags:
      Station: "Canary Wharf Storage Station"
```

**Traffic stays entirely within the Underground network—never surfaces to street level.** Like the DLR tunnels under the Thames, your data never sees daylight, never encounters tourists, and definitely doesn’t stop at every station between Bank and Beckton.

## Platform Screen Doors: Network Security Group Rules (Advanced)

Modern Tube platforms have those lovely glass platform screen doors that only open when a train is present—mostly to prevent drunk people from wandering onto the tracks at Leicester Square on a Friday night. Azure doesn’t have Network ACLs like AWS (because Microsoft decided to keep things simple for once), but Network Security Groups can create similar stateless-style protection using carefully crafted inbound and outbound rules. Think of them as both the turnstiles AND the platform doors combined into one British over-engineering marvel.

**The Difference: Stateful vs Stateless Security**

```yaml
# Azure NSG Rules are STATEFUL (like proper platform doors)
# If you allow inbound traffic, the return traffic is automatically allowed
# Unlike AWS NACLs which are STATELESS (you must explicitly allow both directions)

apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityRule
metadata:
  name: allow-app-tier-from-web
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        network: transport-for-london
    networkSecurityGroupNameSelector:
      matchLabels:
        nsg: central-line
    
    name: AllowWebToApp
    priority: 100  # Lower number = doors open first
    direction: Inbound
    access: Allow
    protocol: Tcp
    sourcePortRange: "*"
    destinationPortRange: "8080"
    sourceAddressPrefix: 10.0.1.0/24  # Northern Line (web tier)
    destinationAddressPrefix: 10.0.2.0/24  # Central Line (app tier)
    
    description: "Platform doors open for trains from Northern Line only"
```

**Creating a “Stateless-style” Configuration** (For the masochists):

If you really want to recreate the AWS NACL experience (why though?), you can create explicit inbound and outbound rules:

```yaml
# Inbound rule - Doors open for incoming trains
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityRule
metadata:
  name: inbound-https
spec:
  forProvider:
    name: AllowHTTPSInbound
    priority: 100
    direction: Inbound
    access: Allow
    protocol: Tcp
    sourcePortRange: "*"
    destinationPortRange: "443"
    sourceAddressPrefix: Internet
    destinationAddressPrefix: "*"

---
# Outbound rule - Doors open for departing trains (return traffic)
# Not strictly necessary in Azure due to stateful nature, but we're being thorough
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityRule
metadata:
  name: outbound-ephemeral
spec:
  forProvider:
    name: AllowEphemeralOutbound
    priority: 100
    direction: Outbound
    access: Allow
    protocol: Tcp
    sourcePortRange: "*"
    destinationPortRange: "1024-65535"  # Ephemeral ports, like random platform numbers
    sourceAddressPrefix: "*"
    destinationAddressPrefix: Internet
    description: "Return traffic to internet, like trains going back to depot"
```

**Default Azure NSG Rules** (The Rules Nobody Reads):

Every NSG comes with default rules you can’t delete, like those announcements nobody listens to:

```
Priority 65000: AllowVNetInBound (All VNet traffic allowed)
  - "Please mind the gap between subnets"

Priority 65001: AllowAzureLoadBalancerInBound 
  - "Health checks from load balancer, stand clear"

Priority 65500: DenyAllInBound
  - "See it, Say it, Sorted - blocks everything else"
```

**Best Practice: Deny by Default**

Unlike the Tube which lets anyone with £2.80 board, your network should deny by default:

```yaml
# Explicit deny rule for RDP (Remote Desktop Protocol)
# Because exposing RDP to internet is like leaving Tube doors open in a tunnel
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkSecurityRule
metadata:
  name: deny-rdp-from-internet
spec:
  forProvider:
    name: DenyRDPFromInternet
    priority: 4096  # High priority = last resort, like emergency stop button
    direction: Inbound
    access: Deny
    protocol: "*"
    sourcePortRange: "*"
    destinationPortRange: "3389"
    sourceAddressPrefix: Internet
    destinationAddressPrefix: "*"
    description: "Platform doors remain firmly shut for RDP - this is not a game"
```

## The Control Room: Crossplane Compositions

Transport for London’s control room at 55 Broadway doesn’t manually operate each signal—they’d need about 47,000 staff and the world’s supply of tea. Instead, they set high-level policies like “run trains every 3 minutes on the Northern Line” and the system orchestrates the details (occasionally successfully). Crossplane Compositions work the same way, minus the inevitable “signal failure at Camden Town.”

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: standard-tube-line-azure
  labels:
    provider: azure
    tfl-approved: "reluctantly"
spec:
  compositeTypeRef:
    apiVersion: network.transportforlondon.io/v1alpha1
    kind: TubeLine
  
  resources:
    # Create the VNet (Underground network)
    - name: vnet
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: VirtualNetwork
        spec:
          forProvider:
            location: UK South
            addressSpace:
              - 10.0.0.0/16
            tags:
              ManagedBy: "Crossplane (more reliable than actual TfL)"
              Status: "Good service (allegedly)"
    
    # Create public subnet (Northern Line - surface level)
    - name: public-subnet
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: Subnet
        spec:
          forProvider:
            addressPrefix: 10.0.1.0/24
            tags:
              Line: "Northern - High Barnet branch"
              Access: "Public (tourists welcome, regrettably)"
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.forProvider.virtualNetworkNameSelector.matchLabels.network
    
    # Create private subnet (Central Line - deep and hot)
    - name: private-subnet
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: Subnet
        spec:
          forProvider:
            addressPrefix: 10.0.2.0/24
            tags:
              Line: "Central - The Human Oven"
              Temperature: "Unacceptable"
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.forProvider.virtualNetworkNameSelector.matchLabels.network
    
    # Create database subnet (Victoria Line - sealed vault)
    - name: database-subnet
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: Subnet
        spec:
          forProvider:
            addressPrefix: 10.0.3.0/24
            delegations:
              - name: postgres-delegation
                properties:
                  serviceName: Microsoft.DBforPostgreSQL/flexibleServers
            tags:
              Line: "Victoria - Actually reliable"
              Access: "Staff only, no tourists"
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.forProvider.virtualNetworkNameSelector.matchLabels.network
    
    # NAT Gateway (Replacement Bus Service)
    - name: nat-gateway-ip
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: PublicIP
        spec:
          forProvider:
            location: UK South
            allocationMethod: Static
            sku: Standard
            tags:
              Service: "Replacement Bus (probably late)"
    
    - name: nat-gateway
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: NATGateway
        spec:
          forProvider:
            location: UK South
            sku:
              - name: Standard
            tags:
              Service: "Victoria Shuttle Service"
              Punctuality: "Questionable"
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.forProvider.publicIpAddressIds[0].selector.matchLabels.gateway
    
    # Security Groups (Turnstiles)
    - name: public-nsg
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: NetworkSecurityGroup
        spec:
          forProvider:
            location: UK South
            tags:
              Purpose: "Northern Line turnstiles"
              Oyster: "Required"
              Contactless: "Also acceptable"
    
    # NSG Rules (The actual barriers)
    - name: allow-https
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: NetworkSecurityRule
        spec:
          forProvider:
            name: AllowHTTPSInbound
            priority: 100
            direction: Inbound
            access: Allow
            protocol: Tcp
            sourcePortRange: "*"
            destinationPortRange: "443"
            sourceAddressPrefix: Internet
            destinationAddressPrefix: "*"
            description: "HTTPS access, like Oyster card tap (usually works)"
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.forProvider.networkSecurityGroupNameSelector.matchLabels.nsg
    
    - name: allow-http
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: NetworkSecurityRule
        spec:
          forProvider:
            name: AllowHTTPInbound
            priority: 110
            direction: Inbound
            access: Allow
            protocol: Tcp
            sourcePortRange: "*"
            destinationPortRange: "80"
            sourceAddressPrefix: Internet
            destinationAddressPrefix: "*"
            description: "HTTP access (will redirect to HTTPS like redirecting to correct platform)"
      patches:
        - type: FromCompositeFieldPath
          fromFieldPath: metadata.name
          toFieldPath: spec.forProvider.networkSecurityGroupNameSelector.matchLabels.nsg
```

**Declare your intent to the Control Room:**

```yaml
apiVersion: network.transportforlondon.io/v1alpha1
kind: TubeLine
metadata:
  name: my-production-network
spec:
  lineName: "Production Northern Line"
  numberOfStations: 5
  publicAccess: true
  heathrowConnection: true  # VPN Gateway to the world
  busService: true  # NAT Gateway enabled
  tourists: tolerated  # Public subnet allows internet traffic
  delays: minimal  # Unlike actual TfL
  engineering-works: scheduled  # With actual notice, revolutionary
```

Crossplane orchestrates building the entire line—tracks, stations, signals, turnstiles, replacement buses, and all. The key difference from actual TfL? **Crossplane actually delivers on time and under budget.**

**Advanced Composition: The Hub-and-Spoke Model**

```yaml
# King's Cross as the central hub
# Multiple lines (spokes) connecting through it
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: hub-and-spoke-network
spec:
  compositeTypeRef:
    apiVersion: network.transportforlondon.io/v1alpha1
    kind: HubAndSpoke
  
  resources:
    # Hub VNet (King's Cross mega-station)
    - name: hub-vnet
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: VirtualNetwork
        spec:
          forProvider:
            location: UK South
            addressSpace:
              - 10.0.0.0/16
            tags:
              Type: "Hub - Kings Cross Central"
              Connections: "All the lines, somehow"
              Confusion: "Maximum"
    
    # Spoke VNets (Satellite lines)
    - name: spoke-vnet-1
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: VirtualNetwork
        spec:
          forProvider:
            location: UK South
            addressSpace:
              - 10.1.0.0/16
            tags:
              Type: "Spoke - Piccadilly Line"
              Destination: "Heathrow eventually"
    
    # VNet Peering (Elizabeth Line connections)
    - name: hub-to-spoke-peering
      base:
        apiVersion: network.azure.upbound.io/v1beta1
        kind: VirtualNetworkPeering
        spec:
          forProvider:
            allowVirtualNetworkAccess: true
            allowForwardedTraffic: true
            allowGatewayTransit: true  # Hub shares its VPN gateway
            tags:
              Connection: "Hub provides transit, like King's Cross"
```

## Signal Systems: Azure Network Watcher

The Tube’s signal system prevents crashes by monitoring train positions in real-time—when it works, which is apparently optional on the Northern Line. In Azure, Network Watcher and NSG Flow Logs provide similar observability, except they actually function most of the time, setting them apart from actual TfL infrastructure.

```yaml
# NSG Flow Logs (Train position tracking and passenger counting)
apiVersion: network.azure.upbound.io/v1beta1
kind: NetworkWatcherFlowLog
metadata:
  name: tube-traffic-monitor
spec:
  forProvider:
    location: UK South
    networkWatcherName: NetworkWatcher_uksouth  # Azure's CCTV network
    resourceGroupName: network-watcher-rg
    
    # Which NSG to monitor
    networkSecurityGroupId: /subscriptions/{sub}/resourceGroups/tfl/providers/Microsoft.Network/networkSecurityGroups/northern-line-nsg
    
    # Storage account for logs (the control room's filing cabinet)
    storageAccountId: /subscriptions/{sub}/resourceGroups/tfl/providers/Microsoft.Storage/storageAccounts/tubemetrics
    
    enabled: true
    
    # Retention - how long we keep the logs
    retentionPolicy:
      - enabled: true
        days: 30  # Longer than it takes to fix a signal failure
    
    # Traffic Analytics (the actual useful bit)
    trafficAnalyticsSettings:
      - enabled: true
        workspaceId: /subscriptions/{sub}/resourceGroups/tfl/providers/Microsoft.OperationalInsights/workspaces/tube-analytics
        workspaceRegion: UK South
        workspaceResourceId: /subscriptions/{sub}/resourceGroups/tfl/providers/Microsoft.OperationalInsights/workspaces/tube-analytics
        intervalInMinutes: 10  # Update every 10 minutes, more frequent than actual service updates
    
    # Flow log format and version
    format:
      - type: JSON
        version: 2
    
    tags:
      Monitor: "Network Traffic Flow"
      Accuracy: "Better than TfL's service updates"
      Status: "Actually working"
```

**What Network Watcher Can Observe:**

**1. Connection Monitor** (Are trains actually running?):

```yaml
apiVersion: network.azure.upbound.io/v1beta1
kind: ConnectionMonitor
metadata:
  name: monitor-northern-to-central
spec:
  forProvider:
    location: UK South
    networkWatcherName: NetworkWatcher_uksouth
    
    # Test groups - like platform inspectors
    testGroups:
      - name: web-to-app-connectivity
        testConfigurations:
          - tcp-test
        sources:
          - northern-line-web-vm
        destinations:
          - central-line-app-vm
    
    # Test configuration - what we're checking
    testConfigurations:
      - name: tcp-test
        protocol: Tcp
        tcpConfiguration:
          - port: 8080
            disableTraceRoute: false
        successThreshold:
          - checksFailedPercent: 5  # Less than 5% failure = "good service" by TfL standards
            roundTripTimeMs: 100  # Faster than an actual Tube journey
    
    tags:
      Purpose: "Monitor if connections actually work"
      Frequency: "Every 60 seconds (revolutionary reliability)"
```

**2. Network Performance Monitor** (How fast are the trains?):

```yaml
# Traffic Analytics insights you can query:
# - Which subnets talk to each other (Northern ↔ Central transfers)
# - Blocked traffic (rejected at turnstiles)
# - Malicious traffic attempts (fare dodgers)
# - Geographic distribution (tourists vs locals)
# - Protocol analysis (HTTP vs HTTPS, TCP vs UDP)
# - Bandwidth consumption (rush hour vs off-peak)
```

**3. IP Flow Verify** (Can this packet even board?):

```yaml
# Using Azure CLI because there's no Crossplane resource yet
# Checks if traffic is allowed between two points

az network watcher test-ip-flow \
  --resource-group tfl \
  --direction Inbound \
  --protocol TCP \
  --local 10.0.1.4:443 \  # Northern Line VM
  --remote 203.0.113.1:443 \  # Some random internet IP
  --vm northern-line-web-01
  
# Response:
# "Access: Allowed" - Train may proceed
# or
# "Access: Denied - Blocked by NSG rule 'DenyAllInbound'" - Platform doors shut
```

**4. Next Hop** (Where does this train go?):

```yaml
# Determines routing path for traffic
# Like asking "Does this train go to Morden?"

az network watcher show-next-hop \
  --resource-group tfl \
  --vm northern-line-web-01 \
  --source-ip 10.0.1.4 \
  --dest-ip 8.8.8.8
  
# Response:
# NextHopType: Internet
# NextHopIpAddress: None
# RouteTableId: /subscriptions/.../routeTables/bank-station-routes
#
# Translation: "Yes, this goes to the internet via Bank station"
```

**5. Packet Capture** (CCTV for network packets):

```yaml
apiVersion: network.azure.upbound.io/v1beta1
kind: PacketCapture
metadata:
  name: investigate-signal-failure
spec:
  forProvider:
    networkWatcherName: NetworkWatcher_uksouth
    resourceGroupName: network-watcher-rg
    
    # Target VM to capture from
    targetResourceId: /subscriptions/{sub}/resourceGroups/tfl/providers/Microsoft.Compute/virtualMachines/suspicious-vm
    
    # How much to capture
    bytesToCapturePerPacket: 0  # Capture entire packet
    totalBytesPerSession: 1073741824  # 1 GB total
    timeLimitInSeconds: 18000  # 5 hours, shorter than an actual investigation
    
    # Where to store captures
    storageLocation:
      - storageAccountId: /subscriptions/{sub}/resourceGroups/tfl/providers/Microsoft.Storage/storageAccounts/investigations
    
    # Filters - like CCTV focusing on specific platforms
    filters:
      - protocol: TCP
        localPort: "22"  # SSH traffic
        remotePort: ""
    
    tags:
      Investigation: "Suspicious SSH attempts"
      Severity: "Like someone trying to break into the driver's cab"
```

**What You Can Observe:**

1. **Which “trains” (packets) are traveling where**
- Northern Line → Central Line transfers
- Traffic to internet via NAT Gateway (replacement bus)
- Private Link connections (DLR exclusive service)
1. **Rejected connections at turnstiles (denied NSG rules)**
- Failed SSH attempts: “Invalid Oyster card, access denied”
- Blocked RDP from internet: “You’re not on the list, mate”
- Port scanning attempts: “Security! We’ve got a suspicious character!”
1. **Bottlenecks at transfer stations (routing issues)**
- Oxford Circus at rush hour (CPU maxed out on firewall)
- Bank station congestion (insufficient NAT Gateway capacity)
- Delays at Earl’s Court (misconfigured route table)
1. **Unusual traffic patterns (security threats)**
- DDoS attack: “Unprecedented passenger volumes on the Northern Line”
- Data exfiltration: “Why is this VM sending 50GB to Romania?”
- Crypto mining: “This instance is using more power than the entire Central Line”

**Alert Examples:**

```yaml
# Alert when NSG blocks suspicious traffic
kind: MetricAlert
metadata:
  name: suspicious-traffic-alert
spec:
  criteria:
    - metricName: "PacketsDroppedDDoS"
      operator: GreaterThan
      threshold: 100
      timeAggregation: Total
  
  description: "Like a crowd of tourists all trying to board at once - probably malicious"
  severity: 2
  frequency: PT5M  # Check every 5 minutes
  windowSize: PT15M  # Over 15 minute window
  
  actions:
    - actionGroupId: /subscriptions/{sub}/resourceGroups/tfl/providers/microsoft.insights/actionGroups/security-team
      webhookProperties:
        message: "Oi! Someone's causing trouble on the Northern Line!"
```

Unlike actual TfL’s “See it, Say it, Sorted,” Azure Network Watcher actually sees it, logs it, alerts you, and provides actionable data. Revolutionary.

## The Night Tube and Regional Networks: Multi-Region High Availability

The Night Tube runs 24/7 on certain lines (Northern, Central, Victoria, Jubilee, and parts of the Piccadilly), which is brilliant until you realize you’re still on the Central Line at 3am questioning your life choices. For high availability in Azure, you run parallel networks across multiple regions—giving you the computing equivalent of having both London Underground AND the Manchester Metrolink, so if one completely collapses (not unlikely), the other can take over.

```yaml
# London Underground (UK South region)
# The main network, busy, expensive, occasionally working
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetwork
metadata:
  name: london-underground
spec:
  forProvider:
    location: UK South  # London and surrounding areas
    resourceGroupNameSelector:
      matchLabels:
        region: london
    addressSpace:
      - 10.1.0.0/16
    tags:
      Region: "London"
      Cost: "Eye-watering"
      Pace: "Frantic"
      Queueing: "Olympic sport"
      Weather: "Overcast with a chance of drizzle"

---
# Manchester Metrolink (UK West region)  
# The backup network, cheaper rent, friendlier people, better music scene
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetwork
metadata:
  name: manchester-metrolink
spec:
  forProvider:
    location: UK West  # Manchester data center
    resourceGroupNameSelector:
      matchLabels:
        region: manchester
    addressSpace:
      - 10.2.0.0/16
    tags:
      Region: "Manchester"
      Cost: "Actually reasonable"
      Football: "Two teams, perpetual rivalry"
      Curry: "Outstanding curry mile"
      Weather: "Rainy (but we're honest about it)"
      Music: "Oasis, Joy Division, The Smiths - need we say more?"

---
# Edinburgh Trams (UK North - hypothetical, but we can dream)
# Scotland's network, different rules, possibly independent
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetwork
metadata:
  name: edinburgh-trams
spec:
  forProvider:
    location: UK North  # If Azure had a Scotland region
    resourceGroupNameSelector:
      matchLabels:
        region: edinburgh
    addressSpace:
      - 10.3.0.0/16
    tags:
      Region: "Scotland"
      Independence: "It's complicated"
      Deep-fried: "Everything"
      Festival: "August is chaos"
      Weather: "Four seasons in one day"
```

**Inter-Regional Connection: The Virgin Trains Approach** (Azure Traffic Manager):

```yaml
# Traffic Manager Profile - The National Rail timetable
# Routes users to the nearest working region
apiVersion: network.azure.upbound.io/v1beta1
kind: TrafficManagerProfile
metadata:
  name: national-rail-interconnect
spec:
  forProvider:
    resourceGroupName: transport-national
    
    # Traffic routing method
    trafficRoutingMethod: Performance  # Route to fastest region, not Birmingham New Street
    
    # DNS configuration
    dnsConfig:
      - relativeName: myapp-uk  # Creates myapp-uk.trafficmanager.net
        ttl: 60  # Cache for 60 seconds, faster than actual train schedules update
    
    # Monitor endpoint health
    monitorConfig:
      - protocol: HTTPS
        port: 443
        path: /health
        intervalInSeconds: 30  # Check every 30 seconds
        toleratedNumberOfFailures: 3  # Allow 3 failures before declaring "service disrupted"
        timeoutInSeconds: 10  # 10 second timeout, generous by UK rail standards
    
    tags:
      Service: "National Rail Routing"
      Reliability: "Better than actual Virgin Trains (RIP)"
      Strikes: "None (bonus!)"

---
# Traffic Manager Endpoint - London
apiVersion: network.azure.upbound.io/v1beta1
kind: TrafficManagerAzureEndpoint
metadata:
  name: london-endpoint
spec:
  forProvider:
    profileNameSelector:
      matchLabels:
        service: national-rail
    
    # Target resource in London
    targetResourceId: /subscriptions/{sub}/resourceGroups/london/providers/Microsoft.Network/publicIPAddresses/london-lb-ip
    
    # Priority and weight
    priority: 1  # London is primary (obviously, it thinks it's the center of the universe)
    weight: 100
    endpointLocation: UK South
    
    tags:
      Region: "London"
      Status: "Primary"
      Attitude: "We're the capital, deal with it"

---
# Traffic Manager Endpoint - Manchester  
apiVersion: network.azure.upbound.io/v1beta1
kind: TrafficManagerAzureEndpoint
metadata:
  name: manchester-endpoint
spec:
  forProvider:
    profileNameSelector:
      matchLabels:
        service: national-rail
    
    targetResourceId: /subscriptions/{sub}/resourceGroups/manchester/providers/Microsoft.Network/publicIPAddresses/manchester-lb-ip
    
    priority: 2  # Backup region (but don't tell Mancunians they're second)
    weight: 100
    endpointLocation: UK West
    
    tags:
      Region: "Manchester"
      Status: "Failover"
      Attitude: "We don't need London anyway"
      Chip-shop: "Superior"
```

**High Availability Pattern:**

```
Traffic Manager (National Rail Timetable)
    ↓
Performance-based routing (Which train gets there fastest?)
    ↓
┌─────────────────────┬──────────────────────┐
│                     │                      │
London (Primary)   Manchester (Failover)   Edinburgh (Future expansion)
UK South           UK West                  UK North (when it exists)
10.1.0.0/16        10.2.0.0/16             10.3.0.0/16
    ↓                  ↓                        ↓
If London fails,   Manchester takes over   Scotland does its own thing
user doesn't notice automatically           (as usual)
```

**Global VNet Peering** (The Chunnel for networks):

```yaml
# Connect London to Manchester via peering
# Like HS2 but actually delivered and under budget
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetworkPeering
metadata:
  name: london-to-manchester
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        region: london
    virtualNetworkNameSelector:
      matchLabels:
        network: london-underground
    
    # The Manchester VNet
    remoteVirtualNetworkId: /subscriptions/{sub}/resourceGroups/manchester-rg/providers/Microsoft.Network/virtualNetworks/manchester-metrolink
    
    # Peering configuration
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true  # Manchester can route through London (begrudgingly)
    allowGatewayTransit: false  # We're not sharing our ExpressRoute, thanks
    useRemoteGateways: false
    
    tags:
      Connection: "North-South Link"
      Politics: "Surprisingly functional"
      Speed: "Faster than HS2 will ever be"

---
# Reciprocal peering (must be bidirectional)
apiVersion: network.azure.upbound.io/v1beta1
kind: VirtualNetworkPeering
metadata:
  name: manchester-to-london
spec:
  forProvider:
    resourceGroupNameSelector:
      matchLabels:
        region: manchester
    virtualNetworkNameSelector:
      matchLabels:
        network: manchester-metrolink
    
    remoteVirtualNetworkId: /subscriptions/{sub}/resourceGroups/london-rg/providers/Microsoft.Network/virtualNetworks/london-underground
    
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    allowGatewayTransit: false
    useRemoteGateways: false
    
    tags:
      Connection: "South-North Link"
      Rivalry: "Friendly (mostly)"
```

**Failover Testing** (Planned engineering works, but with actual notice):

```yaml
# Azure Front Door as alternative to Traffic Manager
# More features, more expensive (like First Class vs Standard)
apiVersion: network.azure.upbound.io/v1beta1
kind: FrontDoor
metadata:
  name: premium-national-rail
spec:
  forProvider:
    resourceGroupName: transport-national
    
    # Backend pools - your regions
    backendPools:
      - name: uk-regions
        backends:
          - address: london-app.azurewebsites.net
            httpPort: 80
            httpsPort: 443
            priority: 1
            weight: 50
            enabled: true
          
          - address: manchester-app.azurewebsites.net
            httpPort: 80
            httpsPort: 443
            priority: 1
            weight: 50
            enabled: true
        
        # Health probe
        healthProbeSettings:
          - path: /health
            protocol: Https
            intervalInSeconds: 30
        
        # Load balancing
        loadBalancingSettings:
          - sampleSize: 4
            successfulSamplesRequired: 2
    
    tags:
      Class: "First"
      Price: "Don't ask"
      Champagne: "Included"
```

**Why Multi-Region?**

1. **Disaster Recovery**: If London’s data center catches fire (not impossible given summer Tube temperatures), Manchester takes over
1. **Performance**: Users in Manchester get routed to Manchester, not forced through London
1. **Compliance**: Scotland might require data sovereignty (devolution!)
1. **Cost Optimization**: Run less critical workloads in cheaper regions (anywhere but London)
1. **Brexit-Proofing**: Spread across UK regions in case of… complications

Unlike actual UK transport infrastructure, this multi-region setup actually works reliably and delivers on time. Revolutionary.

## Putting It All Together: A Complete Passenger Journey

Let’s trace a passenger’s (HTTP request’s) complete journey through your Crossplane-managed Azure Underground network. Think of this as the nightmare journey from Morden to High Barnet via every possible transfer and delay, except this one actually works:

```
1. Passenger arrives at street level (Internet, possibly raining)
   ↓
2. Finds station entrance (DNS resolution to your public IP)
   "Is this the right entrance? The signage is rubbish"
   ↓
3. Enters Northern Line station via turnstile (NSG allows HTTPS:443)
   *tap* "Card accepted" (unlike the usual three attempts)
   ↓
4. Descends to platform (Traffic routes through Application Gateway)
   Escalator probably broken, takes stairs
   ↓
5. Boards train to King's Cross interchange (Load balancer in public subnet)
   Squashed between tourist's backpack and someone's wet umbrella
   ↓
6. Arrives at King's Cross (Traffic distributed by Application Gateway backend pool)
   "This isn't where I wanted to be but here we are"
   ↓
7. Follows confusing signs to Central Line (Route table directs to private subnet)
   Walks for approximately 400 meters underground
   ↓
8. Passes through Central Line turnstile (NSG allows traffic from App Gateway only)
   Security guard checks you came from authorized platform
   ↓
9. Boards Central Line to application station (EC2/VM processes request)
   Temperature: Inexplicably 35°C despite it being January
   ↓
10. Application needs database (Takes staff corridor to Victoria Line)
    NSG allows app tier → database tier connection
    ↓
11. Accesses database station (Azure SQL in deep private subnet)
    Sealed vault, maximum security, no tourists allowed
    ↓
12. Database responds (Returns data back through same route)
    ↓
13. Application processes (Business logic happens on Central Line)
    Still unbearably hot
    ↓
14. Returns via King's Cross (Back through load balancer)
    More walking through endless tunnels
    ↓
15. Back to Northern Line (Response routed to public subnet)
    ↓
16. Exits to street level (Response through Application Gateway to internet)
    *tap out* "Please allow a few moments for this transaction"
    ↓
17. Success! Passenger reaches destination
    Journey time: 8ms (would've been 45 minutes on actual Tube)
```

**Declarative Crossplane Claim for This Entire Journey:**

```yaml
apiVersion: network.transportforlondon.io/v1alpha1
kind: ThreeTierWebApplication
metadata:
  name: my-complex-tube-journey
spec:
  # Web tier (Northern Line - public access)
  webTier:
    publicAccess: true
    allowedPorts: [80, 443]
    protocol: HTTPS
    sslCertificate: lets-encrypt-wildcard
    description: "Northern Line platform, tourists welcome (reluctantly)"
    
  # Application tier (Central Line - private, hot, busy)
  appTier:
    privateSubnet: true
    allowedSources: [webTier]
    instanceCount: 3  # Multiple platforms for peak traffic
    autoScaling: true
    maxTemp: 35C  # Impossible but we try
    description: "Central Line deep tunnel, staff only, inexplicably hot"
  
  # Data tier (Victoria Line - sealed vault)
  dataTier:
    isolatedSubnet: true
    allowedSources: [appTier]
    encryption: "at-rest-and-in-transit"
    backupEnabled: true
    backupRetention: 30  # Days, longer than it takes to fix a signal failure
    description: "Victoria Line database vault, Fort Knox of the Underground"
  
  # Monitoring (CCTV and signal control)
  monitoring:
    flowLogs: true
    networkWatcher: true
    logAnalytics: true
    alerts:
      - name: "high-temperature-alert"
        condition: "Central Line exceeds 30C"
        action: "Nothing, we've given up"
      
      - name: "security-breach"
        condition: "Unauthorized access attempt"
        action: "Lock platform gates, alert security"
      
      - name: "service-disruption"
        condition: "Health probe failing"
        action: "Announce 'minor delays' (actual massive delays)"
  
  # Private endpoints (DLR exclusive service)
  privateEndpoints:
    - service: storage
      reason: "Direct access to document vault"
    - service: sqlServer
      reason: "Bypass public internet, executive privilege"
  
  # Network features
  networkFeatures:
    natGateway: true  # Replacement bus service enabled
    bastionHost: true  # Staff entrance for SSH
    vpnGateway: false  # No Heathrow connection needed
    ddosProtection: standard  # Basic protection against rush hour
    
  # Regional distribution
  regions:
    primary: UK South  # London
    secondary: UK West  # Manchester (failover)
    
  # Cost management
  budget:
    monthly: £500  # About the same as a monthly Travelcard honestly
    alerts: true
    autoShutdown:
      evenings: false  # We run the Night Tube
      weekends: false  # 24/7 service, unlike actual TfL maintenance
  
  # Compliance
  compliance:
    gdpr: enforced
    pci-dss: required  # Payment card data, proper security
    dataResidency: UK  # Brexit compliance
    
  tags:
    Environment: Production
    Owner: "Transport for London (Cloud Division)"
    Status: "Good service (actually true for once)"
    Delays: "None (revolutionary)"
    Engineering-Works: "Scheduled with actual notice (unheard of)"
```

**What Crossplane Actually Builds From This:**

1. **VNet** (10.0.0.0/16) - The entire London Underground network
1. **Three Subnets:**
- Northern Line (10.0.1.0/24) - Public web tier
- Central Line (10.0.2.0/24) - Private app tier, thermostatically challenged
- Victoria Line (10.0.3.0/24) - Isolated database tier
1. **Application Gateway** - King’s Cross interchange with health probes
1. **NSGs** - Turnstiles and platform gates at every entrance
1. **Route Tables** - Transfer station signage (hopefully clearer than actual TfL signs)
1. **NAT Gateway** - Replacement bus service for outbound internet
1. **Private Endpoints** - DLR connections to Azure services
1. **Bastion Host** - Staff entrance for secure SSH
1. **Network Watcher** - CCTV and signal monitoring
1. **Flow Logs** - Recording every passenger movement
1. **Traffic Manager** - National Rail timetable for multi-region
1. **VNet Peering** - Elizabeth Line to Manchester

All configured, secured, monitored, and maintained automatically by Crossplane. No manual Azure Portal clicking, no forgotten NSG rules, no mystery subnets nobody remembers creating.

## Best Practices: Running a Reliable Tube Network

### 1. **Avoid Single Points of Failure (Don’t rely on one tunnel)**

Unlike the actual Piccadilly Line which breaks down if someone sneezes near Cockfosters, design for redundancy:

```yaml
# Multi-AZ deployment (Multiple tunnels under different parts of London)
spec:
  subnets:
    - name: northern-line-zone1
      availabilityZone: 1  # Tunnel under Westminster
      addressPrefix: 10.0.1.0/26
    
    - name: northern-line-zone2
      availabilityZone: 2  # Tunnel under City of London
      addressPrefix: 10.0.1.64/26
    
    - name: northern-line-zone3
      availabilityZone: 3  # Tunnel under Camden
      addressPrefix: 10.0.1.128/26

# If one tunnel floods (not impossible), traffic routes through others
```

### 2. **Implement Defense in Depth (Multiple security layers)**

More barriers than getting into a Central Line carriage at rush hour:

```
Street → Station entrance → Ticket barrier → Platform gate → Train door → Carriage
    ↓          ↓               ↓                ↓               ↓            ↓
Internet → Firewall → App Gateway WAF → NSG → VM firewall → App auth → Data encryption
```

**Azure-specific security layers:**

```yaml
# Layer 1: DDoS Protection (Crowd control at station entrance)
ddosProtectionPlan: Standard  # £2,300/month but worth it when under attack

# Layer 2: Azure Firewall (Main ticket office checkpoint)
azureFirewall: Premium  # With threat intelligence, like having MI5 at the entrance

# Layer 3: Application Gateway WAF (Suspicious behavior detection)
wafPolicy: OWASP_3.2  # Blocks SQL injection like blocking fare dodgers

# Layer 4: NSG (Platform turnstiles)
networkSecurityGroups: Multiple per subnet  # As many barriers as possible

# Layer 5: Azure Bastion (Staff-only entrance)
bastionHost: true  # No direct SSH from internet, civilized access only

# Layer 6: Private Endpoints (DLR exclusive service)
privateLink: Enabled  # Critical services never touch public internet

# Layer 7: Application-level auth (Train conductor checking tickets)
azureAD: Integrated  # Proper authentication, not just hoping for the best
```

### 3. **Monitor Everything (CCTV coverage exceeding even London’s standards)**

```yaml
resources:
  # Network monitoring
  - NetworkWatcher: Enabled in all regions
  - NSG Flow Logs: Every subnet, every NSG
  - Connection Monitor: Test connectivity every 60 seconds
  - Traffic Analytics: Real-time analysis
  
  # Application monitoring
  - Application Insights: Full telemetry
  - Log Analytics: Centralized logging
  - Azure Monitor: Metrics and alerts
  
  # Security monitoring
  - Microsoft Defender for Cloud: Threat detection
  - Sentinel: SIEM for serious incidents
  
  tags:
    Surveillance: "Comprehensive"
    Privacy: "What privacy? This is London"
    GDPR-Compliant: "Technically yes"
```

### 4. **Plan for Peak Hours (Capacity planning for rush hour)**

```yaml
# Application Gateway autoscaling
# Unlike actual Tube which just crams more people in
spec:
  autoscaleConfiguration:
    minCapacity: 2  # Off-peak baseline
    maxCapacity: 10  # Rush hour maximum
  
  # Scale triggers
  rules:
    - metricTrigger:
        metricName: "ApplicationGatewayTotalTime"
        operator: GreaterThan
        threshold: 3000  # 3 seconds response time
        timeAggregation: Average
      scaleAction:
        direction: Increase
        type: ChangeCount
        value: 1  # Add one more platform
        cooldown: PT5M  # Wait 5 minutes before scaling again

# VM Scale Sets (Multiple trains on the same line)
vmScaleSets:
  - minInstances: 3  # Always have three VMs running
    maxInstances: 20  # Scale up during demand
    scaleOutCpuThreshold: 70  # Add VM at 70% CPU
    scaleInCpuThreshold: 30  # Remove VM below 30% CPU
    cooldown: 5 minutes  # Like actual trains, don't rush
```

### 5. **Use Private Links (DLR-style dedicated services)**

Don’t send executive traffic through public stations:

```yaml
# BAD: Database accessible via public endpoint
# Like forcing the CEO to take the Northern Line at 8:30am

databaseConfig:
  publicNetworkAccess: Enabled  # ❌ Everyone on internet can try to connect
  firewallRules:
    - startIP: 0.0.0.0
      endIP: 255.255.255.255  # ❌ "Allow everyone" rule

# GOOD: Database only accessible via Private Link  
# Like providing a private DLR car directly to Canary Wharf

databaseConfig:
  publicNetworkAccess: Disabled  # ✅ No public internet access
  privateEndpoint:
    subnetId: victoria-line-database
    privateDnsZone: privatelink.database.windows.net  # ✅ Internal DNS only
```

### 6. **Tag Everything (Better organization than actual TfL)**

```yaml
tags:
  # Organizational
  Department: "DevOps"
  CostCenter: "Engineering"
  Project: "Platform-Rebuild"
  
  # Technical
  Environment: "Production"
  Tier: "Application"
  Line: "Central"
  
  # Compliance
  DataClassification: "Confidential"
  ComplianceRequirement: "PCI-DSS"
  DataResidency: "UK"
  
  # Operational
  BackupRequired: "Yes"
  MonitoringLevel: "Premium"
  SLA: "99.95%"
  
  # Humour (optional but recommended)
  Temperature: "Too-bloody-hot"
  Delays: "None-today-miraculously"
  TouristDensity: "Moderate"
  Status: "Good-service-for-once"
```

### 7. **Implement Proper DNS (Unlike TfL’s station signage)**

```yaml
# Azure Private DNS Zones
# So services can find each other without asking for directions

apiVersion: network.azure.upbound.io/v1beta1
kind: PrivateDnsZone
metadata:
  name: internal-tfl-network
spec:
  forProvider:
    resourceGroupName: network-rg
    name: tfl.internal  # Internal domain
    
    tags:
      Purpose: "Internal service discovery"
      Clarity: "Actually clear, unlike station signs"

# DNS Zone Link to VNet
apiVersion: network.azure.upbound.io/v1beta1
kind: PrivateDnsZoneVirtualNetworkLink
metadata:
  name: link-dns-to-underground
spec:
  forProvider:
    privateDnsZoneName: tfl.internal
    virtualNetworkId: london-underground-vnet-id
    registrationEnabled: true  # Auto-register VM hostnames
    
# Now VMs can reach each other via:
# web-server-01.tfl.internal
# app-server-01.tfl.internal  
# db-server-01.tfl.internal
#
# Much clearer than "Third platform on left past the pasty shop"
```

### 8. **Cost Optimization (Unlike actual TfL projects)**

```yaml
# Use Azure Cost Management
costManagement:
  budgets:
    - name: "monthly-network-budget"
      amount: 500  # £500/month
      timeGrain: Monthly
      alerts:
        - threshold: 80  # Alert at 80% spend
          contactEmails: ["finance@tfl.internal"]
        - threshold: 100  # Panic at 100%
          contactEmails: ["everyone@tfl.internal"]
  
  # Cost-saving strategies
  strategies:
    # Stop dev/test environments outside working hours
    - autoShutdown:
        enabled: true
        time: "19:00"
        timezone: "GMT Standard Time"
        notification: 30-minutes-before
    
    # Use reserved instances for predictable workloads
    - reservedInstances:
        commitment: 3-years  # Long-term like a season ticket
        discount: 62%  # Actually significant savings
    
    # Right-size VMs (don't run D32s_v3 when B2ms suffices)
    - rightSizing:
        enabled: true
        recommendations: weekly
        autoImplement: false  # Review first, we're not monsters
    
    # Use spot instances for batch workloads
    - spotInstances:
        maxPrice: -1  # Up to pay-as-you-go price
        evictionPolicy: Deallocate
        useCase: "Non-critical batch processing"
```

## Common Mistakes: Underground Disasters to Avoid

### ❌ **Allowing direct internet to private subnets**

```yaml
# DON'T DO THIS - Victoria Line with emergency exit to street level
kind: Subnet
spec:
  addressPrefix: 10.0.3.0/24
  routeTable:
    - name: direct-internet  # ❌ WRONG
      route:
        addressPrefix: 0.0.0.0/0
        nextHopType: Internet  # ❌ Database subnet going directly to internet

# This is like putting an unsecured fire exit in the vault
# Databases should NEVER have direct internet routes
```

**Why this is terrible:**

- Database exposed to entire internet (billions of potential attackers)
- Like leaving the Crown Jewels accessible from Oxford Street
- Violates every compliance framework (PCI-DSS, GDPR, common sense)

**Correct approach:**

```yaml
# Database subnet has NO internet route
# If it needs outbound connectivity, use NAT Gateway
kind: Subnet
spec:
  addressPrefix: 10.0.3.0/24
  routeTable:
    - name: internal-only
      routes:
        - addressPrefix: 10.0.0.0/16
          nextHopType: VnetLocal  # ✅ Internal VNet traffic only
```

### ❌ **Overly permissive NSG rules**

```yaml
# DON'T - Removing all turnstiles
kind: NetworkSecurityRule
spec:
  name: "allow-everything-because-easier"
  priority: 100
  sourceAddressPrefix: "*"  # ❌ From anywhere
  sourcePortRange: "*"  # ❌ Any port
  destinationAddressPrefix: "*"  # ❌ To anywhere
  destinationPortRange: "*"  # ❌ Any destination port
  protocol: "*"  # ❌ Any protocol
  access: Allow  # ❌ Come on in, everyone!

# This is security theatre, not security
# Like having turnstiles that are permanently open
```

**Why this defeats the purpose:**

- Might as well not have NSGs at all
- Every service exposed to every other service
- Lateral movement heaven for attackers
- Compliance auditor’s nightmares made real

**Correct approach:**

```yaml
# Principle of least privilege - like proper turnstiles
kind: NetworkSecurityRule
spec:
  name: "allow-web-to-app-only"
  priority: 100
  sourceAddressPrefix: 10.0.1.0/24  # ✅ Only web tier
  sourcePortRange: "*"
  destinationAddressPrefix: 10.0.2.0/24  # ✅ Only app tier
  destinationPortRange: "8080"  # ✅ Specific port
  protocol: Tcp  # ✅ Specific protocol
  access: Allow
  description: "Web tier to app tier, authenticated traffic only"
```

### ❌ **Forgetting return routes**

```yaml
# DON'T - One-way turnstiles
kind: NetworkSecurityRule
spec:
  # Inbound rule allowing traffic
  name: "allow-inbound-http"
  direction: Inbound
  access: Allow
  
  # But no corresponding outbound rule allowing response
  # NSGs are stateful so you don't NEED explicit outbound
  # BUT if you manually deny outbound, you've broken it

kind: NetworkSecurityRule
spec:
  name: "deny-all-outbound"  # ❌ This breaks return traffic
  priority: 4096
  direction: Outbound
  access: Deny
  sourceAddressPrefix: "*"
  destinationAddressPrefix: "*"
```

**Why this is a problem:**

- Requests arrive but responses can’t leave
- Like a Tube station where you can enter but can’t exit
- Platform becomes dangerously overcrowded
- Users experience timeout errors

**Remember:** Azure NSGs are **stateful** - if you allow inbound traffic, return traffic is automatically allowed. Don’t fight this by adding explicit denies.

### ❌ **Not using subnets properly (One massive shared platform)**

```yaml
# DON'T - Everything in one huge subnet
kind: VirtualNetwork
spec:
  addressSpace:
    - 10.0.0.0/16
  subnets:
    - name: everything-subnet  # ❌ One subnet for all services
      addressPrefix: 10.0.0.0/16
      
# All VMs in same subnet:
# - Web servers
# - App servers  
# - Databases
# - Admin jump boxes
# - Random test VMs
# 
# Like putting First Class, Standard, and the toilets all in the same carriage
```

**Why this is problematic:**

- Can’t apply different NSG rules per tier
- No network segmentation for defense in depth
- Lateral movement is trivial
- Can’t use subnet delegation for PaaS services
- Compliance nightmares

**Correct approach:**

```yaml
# Proper subnet segregation
subnets:
  - name: web-tier
    addressPrefix: 10.0.1.0/24  # ✅ Separate subnet
    nsg: web-nsg  # Different security rules
    
  - name: app-tier
    addressPrefix: 10.0.2.0/24  # ✅ Separate subnet
    nsg: app-nsg
    
  - name: data-tier
    addressPrefix: 10.0.3.0/24  # ✅ Separate subnet
    nsg: data-nsg
    delegation: Microsoft.DBforPostgreSQL/flexibleServers
    
  - name: management
    addressPrefix: 10.0.100.0/24  # ✅ Separate management subnet
    nsg: bastion-nsg
```

### ❌ **Exposing management ports to internet**

```yaml
# DON'T - SSH/RDP from anywhere
kind: NetworkSecurityRule
spec:
  name: "allow-ssh-from-internet"  # ❌ Terrible idea
  sourceAddressPrefix: Internet
  destinationPortRange: "22"
  access: Allow
  
# This is like putting a "Staff Entrance" sign on Oxford Circus
# with no actual security
# Guaranteed to be brute-forced within minutes
```

**Why this is asking for trouble:**

- Constant brute force attempts (SSH password guessing)
- Exposed to every script kiddie on the planet
- Compliance violation in most frameworks
- Like leaving your front door wide open with a “Please Rob Me” sign

**Correct approach - Use Azure Bastion:**

```yaml
# Azure Bastion - Proper staff entrance with security
apiVersion: network.azure.upbound.io/v1beta1
kind: BastionHost
metadata:
  name: tfl-bastion
spec:
  forProvider:
    resourceGroupName: network-rg
    location: UK South
    
    # Dedicated subnet for Bastion (must be named this)
    ipConfigurations:
      - name: bastion-ip-config
        subnetIdSelector:
          matchLabels:
            subnet: AzureBastionSubnet  # Must be this exact name
        publicIpAddressIdSelector:
          matchLabels:
            purpose: bastion
    
    # No need for NSG rules allowing SSH/RDP from internet
    # Bastion handles authentication and provides browser-based access
    
    tags:
      Purpose: "Secure admin access"
      Better-than: "Opening port 22 to 0.0.0.0/0"
```

### ❌ **Not planning IP address space**

```yaml
# DON'T - Random IP ranges without thought
vnet1:
  addressSpace: 10.0.0.0/16  # 65,536 IPs
  
vnet2:
  addressSpace: 10.0.0.0/20  # ❌ OVERLAPS with vnet1!
  
# Can't peer these VNets - conflicting address space
# Like building two Tube lines in the same tunnel
```

**Why this is a disaster:**

- Can’t peer VNets with overlapping IP spaces
- Can’t connect to on-premises network if ranges conflict
- Painful to fix later (requires rebuilding networks)
- Like discovering your basement extension overlaps with your neighbour’s

**Correct approach - Plan address space:**

```yaml
# Corporate IP plan (actually organized)
on-premises: 10.0.0.0/8  # Reserved for on-prem (don't use)

# Azure regions
london-vnet: 10.1.0.0/16  # UK South - 65,536 IPs
manchester-vnet: 10.2.0.0/16  # UK West - 65,536 IPs
dev-vnet: 10.10.0.0/16  # Development environment
test-vnet: 10.11.0.0/16  # Testing environment

# No overlaps, can peer any combination
# Can extend without conflicts
# Room for growth
```

### ❌ **Manual configuration drift (Clicking in Azure Portal)**

```yaml
# What actually happened:
# 1. DevOps creates network via Crossplane
# 2. Developer needs "quick fix" - adds NSG rule via Portal
# 3. Someone else modifies route table in Portal
# 4. Security team adds firewall rules manually
# 5. Nobody documents anything
# 
# Result: Crossplane YAML doesn't match reality
# Like the official Tube map not matching actual routes
```

**Why this causes problems:**

- Configuration drift between code and reality
- Crossplane reconciliation might revert manual changes
- No audit trail of who changed what
- Impossible to recreate environment
- “Works on my Azure subscription” syndrome

**Correct approach - GitOps all the way:**

```yaml
# All changes via Git pull requests
process:
  1. Developer needs NSG rule change
  2. Creates branch: feature/allow-new-service
  3. Modifies Crossplane YAML
  4. Opens pull request
  5. Security team reviews
  6. DevOps approves
  7. CI/CD pipeline applies changes
  8. Change is in Git history
  9. Can be rolled back if needed
  10. Fully audited
  
# Like TfL having proper change control
# (They don't, but we can dream)
```

### ❌ **Ignoring Azure Service Tags**

```yaml
# DON'T - Hardcode IP addresses for Azure services
kind: NetworkSecurityRule
spec:
  name: "allow-storage"
  sourceAddressPrefix: "20.150.0.0/16"  # ❌ Azure Storage IPs (will change!)
  destinationPortRange: "443"
  access: Allow

# Azure's IP ranges change regularly
# This rule will break when Microsoft updates ranges
# Like memorizing bus routes only for them to change weekly
```

**Correct approach - Use Service Tags:**

```yaml
kind: NetworkSecurityRule
spec:
  name: "allow-storage-via-tag"
  sourceAddressPrefix: Storage.UKSouth  # ✅ Service Tag
  destinationPortRange: "443"
  access: Allow
  
# Service Tags automatically update
# Covers all Storage IPs in UK South region
# Microsoft maintains it, not you

# Available Service Tags:
# - Storage
# - SQL  
# - AzureKeyVault
# - AzureActiveDirectory
# - Internet
# And many more...
```

**Remember:** If you’re manually clicking in the Azure Portal to configure networking, you’re doing it wrong. Crossplane exists precisely so you don’t have to do that. Let the automation handle it, like Transport for London should’ve automated their announcements instead of having someone say “minor delays” 473 times per day.

## Conclusion: Mind the Gap

Just as Transport for London doesn’t expect passengers to understand signal systems, track switches, power distribution, and the inexplicable heat on the Central Line, Crossplane Networking lets you declare your network requirements without drowning in Azure’s 47 different ways to configure a subnet.

You declare:

```yaml
"I need a three-tier web application with public web servers, 
private application servers, isolated databases, proper monitoring,
and for the love of all that's holy, can it actually work reliably
unlike the Northern Line?"
```

Crossplane responds:

```
"Right, I'll build you:
- Northern Line for public web (with actual functioning escalators)
- Central Line for private apps (regrettably still hot)
- Victoria Line for databases (sealed tighter than a banker's wallet)
- Proper turnstiles, platform gates, signal systems
- CCTV coverage that would make George Orwell blush
- Replacement bus service for outbound traffic
- DLR connections for your executive services
- Multi-region setup so Manchester can take over if London floods
- All properly monitored, secured, and maintained
- Please mind the gap between your resources."
```

Your Azure infrastructure becomes a well-orchestrated transit system—secure, observable, and declarative. Unlike actual Transport for London, it:

✅ Runs on time  
✅ Stays within budget  
✅ Provides accurate service updates  
✅ Actually has working escalators  
✅ Temperature stays below 30°C  
✅ Gives advance notice of engineering works  
✅ Doesn’t randomly close platforms “for your safety”  
✅ Documentation makes sense  
✅ The Circle Line is actually circular (in network topology)

**The Azure Network Journey:**

```
You write 50 lines of YAML
  ↓
Crossplane creates:
  ✓ Virtual Networks
  ✓ Subnets (properly segmented)
  ✓ NSGs (with sensible rules)
  ✓ Route Tables (with clear signage)
  ✓ Application Gateways
  ✓ NAT Gateways
  ✓ Private Endpoints
  ✓ Network Watcher
  ✓ Flow Logs
  ✓ Monitoring & Alerts
  ↓
Result: Production-grade network infrastructure
Time: Minutes, not months
Budget overruns: None (unheard of in UK infrastructure)
Delays: None (revolutionary)
Confused tourists: Fewer (the YAML is clearer than TfL signs)
```

**Next Steps:**

1. **Map your current network to Tube lines**: Identify which subnets are public (Northern Line surface routes) vs private (Victoria Line deep tunnels)
1. **Implement security layers**: Add both turnstiles (NSGs) and platform gates (more NSGs because Azure doesn’t have NACLs, but that’s fine, really)
1. **Create Compositions**: Build reusable network patterns like “standard three-tier” or “microservices mesh with more security than MI6”
1. **Enable comprehensive monitoring**: Install the signal system (Network Watcher, Flow Logs) and actually pay attention to the alerts
1. **Practice GitOps**: Make your Tube map (network topology) version-controlled and declarative. No more manual Portal clicking like some sort of savage.
1. **Tag everything**: Better organization than actual TfL (low bar)
1. **Use Private Link**: Keep executive traffic off public transport
1. **Plan for peak hours**: Auto-scaling so your infrastructure doesn’t become like the Northern Line at 8:30am
1. **Cost optimization**: Unlike HS2, actually deliver under budget
1. **Test disaster recovery**: Ensure Manchester can handle the load when London inevitably has “severe disruption”

**Final Thought:**

Remember: **Good network design, like good public transport, is invisible when it works perfectly.** Passengers (users) shouldn’t think about the complexity—they should just arrive at their destination safely, efficiently, and without being delayed by “an earlier incident at Bank” or “signal failures” or “a customer taken ill” or any of the other creative excuses TfL has in its repertoire.

The key difference between Azure networking with Crossplane and the actual London Underground?

**Crossplane actually delivers good service.**

Now go build your Underground network. And please, mind the gap between your cloud resources.

*Stands clear of the closing doors, please.*

-----

**Disclaimer:** No actual Transport for London infrastructure was harmed in the making of this article. The Northern Line, however, continues to harm itself through sheer determination and the laws of thermodynamics.

**P.S.:** If you enjoyed this metaphor and found yourself nodding along whilst simultaneously feeling personally attacked as a Londoner, congratulations—you understand both cloud networking and the daily torment of the Tube commute. You’re basically a dual-certified expert now.

*“This article is currently delayed due to signal failures. We apologize for any inconvenience.”*  
— Not Transport for London, because this actually arrived on time.

-----

*What network metaphor would you like to see next? Crossplane Multi-Cloud as the Eurostar? Kubernetes Service Mesh as the M25 motorway (circular, congested, nobody knows why they’re on it)? Let me know in the comments!* 🚇

**Tags:** #crossplane #kubernetes #networking #azure #infrastructure #devops #iac #britishhumour

-----

## Further Reading

### Crossplane Documentation

- [Crossplane Official Docs](https://docs.crossplane.io) - The actual manual, unlike TfL’s “guides”
- [Upbound Azure Provider](https://marketplace.upbound.io/providers/upbound/provider-azure-network/) - Azure networking resources
- [Crossplane Compositions Deep Dive](https://docs.crossplane.io/latest/concepts/compositions/) - How to orchestrate it all

### Azure Networking Resources

- [Azure Virtual Network Documentation](https://docs.microsoft.com/en-us/azure/virtual-network/) - Microsoft’s take on networking
- [Azure Network Security Best Practices](https://docs.microsoft.com/en-us/azure/security/fundamentals/network-best-practices) - Actually sensible advice
- [Azure Well-Architected Framework - Network](https://docs.microsoft.com/en-us/azure/architecture/framework/security/design-network) - How to not cock it up
- [Azure Network Watcher](https://docs.microsoft.com/en-us/azure/network-watcher/) - Your CCTV system
- [Azure Private Link](https://docs.microsoft.com/en-us/azure/private-link/) - The DLR of cloud services

### Transport for London (For comparison)

- [TfL Service Updates](https://tfl.gov.uk/tube-dlr-overground/status/) - “Minor delays” and other creative fiction
- [Tube Map](https://tfl.gov.uk/maps/track/tube) - The most optimistic diagram in London
- [Oyster Card](https://tfl.gov.uk/fares/how-to-pay-and-where-to-buy-tickets-and-oyster/oyster) - Still somehow more reliable than contactless

### British Humour References

- [Why the Central Line is So Hot](https://www.ianvisits.co.uk/articles/why-is-the-tube-so-hot-12246/) - Science explains the sauna
- [History of the Northern Line Split](https://en.wikipedia.org/wiki/Northern_line) - How one line became seventeen
- [The Circle Line That Isn’t Circular](https://www.timeout.com/london/news/the-circle-line-is-no-longer-a-circle-120320) - TfL giving up on geometry

-----

## About the Author

Willem van Heemstra is a Cloud Engineer specializing in Infrastructure-as-Code, Kubernetes, and Crossplane implementations. After years of suffering on the London Underground (Northern Line, mainly), he believes complex technical concepts are best explained through metaphors that trigger both understanding and PTSD flashbacks of the morning commute.

He once got stuck on a broken-down Central Line train for 47 minutes in the tunnel between Holborn and Chancery Lane, during which time he designed an entire Azure network architecture on his phone. The network worked perfectly. The air conditioning on the train did not.

Connect with him on [LinkedIn](https://www.linkedin.com/in/willemvanheemstra) or follow his articles on [Dev.to](https://dev.to/willemvanheemstra) where he continues his mission to make cloud infrastructure less confusing than TfL’s signage.

-----

*This article is part of the “Infrastructure Through Everyday British Suffering” series:*

1. **Crossplane Basics**: Fast-Food Restaurant Ordering (Because we queue for everything)
1. **Crossplane Security**: Defending Your Cyber-Vegetable Garden Against Rabbits (British gardening obsession)
1. **Crossplane with Crossview**: The Monopoly Board (British board game dominance)
1. **Crossplane E2E Testing**: IKEA Furniture Assembly (Swedish, but we’ve all been to Wembley IKEA)
1. **Crossplane Networking**: Mind the Gap - The London Underground (You are here, delayed)

**Coming Soon:**

- *Crossplane Multi-Cloud*: The Eurostar Experience (Britain → Europe connectivity drama)
- *Kubernetes Pod Scheduling*: Trying to Get a GP Appointment (Impossible resource allocation)
- *Service Mesh*: The M25 Motorway (Circular, confusing, perpetually congested)
- *GitOps*: The British Queue (Orderly, systematic, occasionally violent if someone cuts in)

-----

## Acknowledgments

Special thanks to:

- Transport for London, for providing decades of material for this article through their consistent service disruptions
- The Northern Line, for teaching us patience
- The Central Line, for teaching us heat tolerance
- The Victoria Line, for showing that occasionally things do work in London
- The District Line, for… existing, I suppose
- Every tourist who ever stood on the left side of the escalator at Holborn

And finally, to that one busker at King’s Cross who plays the saxophone beautifully despite the acoustics being absolutely terrible. You make the delays slightly more bearable, mate.

-----

**Reader Exercise:**

Map your current Azure network to Tube lines:

- Which services are in your “Northern Line” (public-facing)?
- What’s lurking in your “Central Line” (private applications, inexplicably resource-intensive)?
- How well-sealed is your “Victoria Line” (database tier)?
- Do you have a “Replacement Bus Service” (NAT Gateway) that actually works?
- When was the last time you checked if your “DLR” (Private Endpoints) was actually running?

Share your infrastructure’s “Tube map” in the comments, and together we can diagnose which lines need urgent engineering works.

*Please stand clear of the closing doors.*

-----

**Epilogue: A Note on British Sarcasm**

If you’re reading this and thinking “Blimey, this author really doesn’t like Transport for London,” you’d be partly right. But here’s the thing: like every Londoner, I simultaneously despise and depend on the Tube. It’s overcrowded, overpriced, and over-heated, yet somehow it’s still the fastest way to get across London.

Similarly, Azure networking can seem overcomplicated and overly complex—but when properly configured with Crossplane, it’s actually brilliant. The analogy works because both systems:

1. Are incredibly complex underneath
1. Work remarkably well despite the chaos
1. Require specialized knowledge to navigate
1. Benefit enormously from good tooling
1. Are best when you don’t have to think about them

So next time you’re on the Tube, squashed between a tourist’s oversized rucksack and someone’s soggy umbrella, remember: somewhere in an Azure data center, packets are having exactly the same experience trying to navigate through poorly configured network security groups.

The difference is, with Crossplane, you can fix your network. We’re still waiting for TfL to fix the air conditioning on the Central Line.

*Estimated reading time: 47 minutes (about the same as Northern Line delays)*
