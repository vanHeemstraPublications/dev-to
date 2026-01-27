---
title: "Crossplane Networking: Mind the Gap Between Your Cloud Resources“
published: false
description: Understanding Crossplane v2 networking through the lens of the London Underground
tags: [kubernetes, crossplane, networking, devops]
series: "Infrastructure-as-Code Adventures"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/crossplane-infrastructure-mind-the-gap.png"
organization: "the-software-s-journey"
---

*How Crossplane v2 manages your cloud network infrastructure like Transport for London manages the Tube*

## Introduction

Ever stood on a London Underground platform, watching the intricate dance of trains arriving, departing, and transferring passengers across the city? Behind that seamless experience is a masterfully orchestrated network of tracks, signals, tunnels, and security checkpoints.

Crossplane Networking in version 2 works remarkably similar to the Tube: you declare where your “passengers” (data packets) need to go, and Crossplane builds and manages the entire transit infrastructure—tracks, transfers, turnstiles, and all—to get them there safely and efficiently.

Let’s explore how Crossplane Networking transforms your cloud infrastructure into a world-class metro system.

## The Underground Map: Your Network Topology

When you look at the iconic London Underground map, you see colored lines connecting stations across the city. In Crossplane Networking, your infrastructure has a similar topology:

### **VPCs = The Entire Underground Network**

Your Virtual Private Cloud (VPC) is like the entire London Underground network—a self-contained transit system with its own tracks, stations, and rules.

```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPC
metadata:
  name: london-underground-vpc
spec:
  forProvider:
    cidrBlock: 10.0.0.0/16
    region: eu-west-2
    tags:
      Name: "London Underground Network"
      Network: "Production"
```

### **Subnets = Different Tube Lines**

Just as the Tube has the Circle Line, Northern Line, and Piccadilly Line, your VPC has subnets—each serving different purposes and zones:

```yaml
# The Northern Line (Public Subnet - Direct street access)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
metadata:
  name: northern-line-public
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    cidrBlock: 10.0.1.0/24
    availabilityZone: eu-west-2a
    mapPublicIpOnLaunch: true
    tags:
      Name: "Northern Line - Public Web Tier"
      Line: "Public-Facing"

---
# The Central Line (Private Subnet - Application tier)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
metadata:
  name: central-line-private
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    cidrBlock: 10.0.2.0/24
    availabilityZone: eu-west-2a
    tags:
      Name: "Central Line - Application Services"
      Line: "Private-Backend"

---
# The Victoria Line (Private Subnet - Database tier)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Subnet
metadata:
  name: victoria-line-database
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    cidrBlock: 10.0.3.0/24
    availabilityZone: eu-west-2a
    tags:
      Name: "Victoria Line - Database Tier"
      Line: "Private-Data"
```

**The Pattern:**

- **Northern Line (Public)**: Web servers with street-level access (internet gateway)
- **Central Line (Private)**: Application servers requiring transfers to reach the surface
- **Victoria Line (Deep Private)**: Databases buried deep underground with restricted access

## Stations and Platforms: Your Services

Each station on the Tube represents a service in your infrastructure. Some are busy interchange stations (load balancers), others are quiet local stops (single instances).

```yaml
# King's Cross Station (Load Balancer - Major interchange)
apiVersion: elbv2.aws.upbound.io/v1beta1
kind: LB
metadata:
  name: kings-cross-lb
spec:
  forProvider:
    region: eu-west-2
    loadBalancerType: application
    subnets:
      - name: northern-line-public
    tags:
      Station: "Kings Cross"
      Type: "Major Interchange"
```

## Turnstiles and Oyster Readers: Security Groups

Just as you can’t board a Tube train without tapping your Oyster card at the turnstile, packets can’t enter your resources without passing through security groups.

```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: SecurityGroup
metadata:
  name: northern-line-turnstile
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    description: "Northern Line turnstiles - Public web access"
    ingress:
      # Oyster card tap - Allow HTTPS from anywhere
      - fromPort: 443
        toPort: 443
        protocol: tcp
        cidrBlocks:
          - 0.0.0.0/0
        description: "Public HTTPS access like Oyster tap-in"
      
      # Staff entrance - SSH from admin network only
      - fromPort: 22
        toPort: 22
        protocol: tcp
        cidrBlocks:
          - 10.0.100.0/24
        description: "Staff-only SSH access"
    
    egress:
      # Exit turnstiles - Allow all outbound
      - fromPort: 0
        toPort: 0
        protocol: -1
        cidrBlocks:
          - 0.0.0.0/0
        description: "Exit turnstile - all outbound allowed"
    
    tags:
      Purpose: "Northern Line Access Control"
```

**Security Zones by Line:**

- **Northern Line (Public)**: Open turnstiles accepting passengers from the street (ports 80, 443 open)
- **Central Line (Semi-Private)**: Only accepts transfers from Northern Line (only internal traffic)
- **Victoria Line (Restricted)**: Staff-only access, no public entry (database ports restricted to app tier)

## Transfer Stations: Route Tables

Transfer stations like Bank or King’s Cross allow passengers to switch between lines. Route tables serve the same purpose—directing traffic between subnets.

```yaml
# Bank Station Route Table (Major Transfer Point)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: RouteTable
metadata:
  name: bank-station-routes
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    tags:
      Station: "Bank Transfer"
      Type: "Interchange"

---
# Route to Internet Gateway (Exit to street level)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: Route
metadata:
  name: route-to-street
spec:
  forProvider:
    routeTableIdRef:
      name: bank-station-routes
    destinationCidrBlock: 0.0.0.0/0
    gatewayIdRef:
      name: street-level-gateway
```

**Transfer Patterns:**

```
Northern Line → Internet Gateway = Direct exit to street level
Central Line → NAT Gateway → Internet = Must transfer at designated station
Victoria Line → No external access = Sealed deep tunnel, staff corridors only
```

## The Piccadilly Line to Heathrow: Internet Gateway

The Piccadilly Line connects central London directly to Heathrow Airport—your gateway to the outside world. In network terms, this is your Internet Gateway.

```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: InternetGateway
metadata:
  name: heathrow-gateway
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    tags:
      Gateway: "Heathrow International"
      Purpose: "Direct internet access"
```

**Only public subnets (Northern Line) get direct routes to Heathrow.** Private subnets must transfer through other stations.

## The Shuttle Service: NAT Gateway

Not all Tube lines go directly to the airport. Some passengers must take a shuttle bus from a transfer station. This is your NAT Gateway—a designated transfer point for private subnet traffic heading to the internet.

```yaml
# Victoria Station Shuttle (NAT Gateway)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: NATGateway
metadata:
  name: victoria-station-shuttle
spec:
  forProvider:
    subnetIdRef:
      name: northern-line-public  # NAT must be in public subnet
    allocationIdRef:
      name: shuttle-elastic-ip
    tags:
      Service: "Victoria Shuttle to Internet"
```

**The Journey:**

```
Private subnet (Central Line) 
  → NAT Gateway (Victoria Shuttle) 
  → Internet Gateway (Heathrow) 
  → Internet
```

Private resources can’t go directly to Heathrow; they must catch the shuttle from Victoria Station.

## The Elizabeth Line Connection: VPC Peering

The new Elizabeth Line connects previously separate networks. In Crossplane, VPC Peering creates these cross-network connections.

```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPCPeeringConnection
metadata:
  name: elizabeth-line-connection
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    peerVpcIdRef:
      name: crossrail-vpc
    peerRegion: eu-west-2
    tags:
      Connection: "Elizabeth Line"
      Purpose: "East-West integration"
```

**Use Cases:**

- Connect production VPC (London Underground) with development VPC (Crossrail)
- Link different regional networks (London ↔ Manchester)
- Create secure tunnels between isolated environments

## The DLR Private Railway: AWS PrivateLink

The Docklands Light Railway (DLR) is a separate, more exclusive system connecting specialized areas. AWS PrivateLink works similarly—creating private, high-security connections to AWS services without touching the public internet.

```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPCEndpoint
metadata:
  name: dlr-to-s3
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    serviceName: com.amazonaws.eu-west-2.s3
    vpcEndpointType: Gateway
    routeTableIds:
      - name: victoria-line-routes
    tags:
      Service: "DLR Private S3 Access"
```

**Private connections to AWS services:**

- S3 buckets via Gateway endpoint
- DynamoDB via Gateway endpoint
- Lambda, SNS, SQS via Interface endpoints

Traffic stays entirely within the Underground network—never surfaces to street level.

## Network ACLs: Platform Gates

Modern Tube platforms have platform edge doors that only open when a train is present. Network ACLs (NACLs) work similarly—they’re stateless barriers that control what traffic can even approach your subnet’s platform.

```yaml
apiVersion: ec2.aws.upbound.io/v1beta1
kind: NetworkACL
metadata:
  name: platform-gates-central-line
spec:
  forProvider:
    vpcIdRef:
      name: london-underground-vpc
    tags:
      Line: "Central Line Platform Safety"

---
# Inbound Platform Gate Rules
apiVersion: ec2.aws.upbound.io/v1beta1
kind: NetworkACLRule
metadata:
  name: allow-http-to-platform
spec:
  forProvider:
    networkAclIdRef:
      name: platform-gates-central-line
    ruleNumber: 100
    protocol: 6  # TCP
    ruleAction: allow
    cidrBlock: 0.0.0.0/0
    fromPort: 80
    toPort: 80
    egress: false
```

**Security Groups vs NACLs:**

- **NACLs (Platform Gates)**: Subnet-level, stateless, numbered priority rules
- **Security Groups (Turnstiles)**: Instance-level, stateful, allow-only rules

Think of it as two layers of security: platform gates prevent dangerous items from reaching the platform, while turnstiles check individual passenger credentials.

## The Control Room: Crossplane Compositions

Transport for London’s control room doesn’t manually operate each signal—they set high-level policies and the system orchestrates the details. Crossplane Compositions work the same way.

```yaml
apiVersion: apiextensions.crossplane.io/v1
kind: Composition
metadata:
  name: standard-tube-line
spec:
  compositeTypeRef:
    apiVersion: network.example.com/v1alpha1
    kind: TubeLine
  
  resources:
    # Create the VPC (Underground network)
    - name: vpc
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: VPC
        spec:
          forProvider:
            cidrBlock: 10.0.0.0/16
    
    # Create public subnet (Surface line)
    - name: public-subnet
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: Subnet
        spec:
          forProvider:
            cidrBlock: 10.0.1.0/24
            mapPublicIpOnLaunch: true
    
    # Create private subnet (Deep tunnel)
    - name: private-subnet
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: Subnet
        spec:
          forProvider:
            cidrBlock: 10.0.2.0/24
    
    # Internet Gateway (Airport connection)
    - name: internet-gateway
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: InternetGateway
    
    # NAT Gateway (Shuttle service)
    - name: nat-gateway
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: NATGateway
    
    # Security Groups (Turnstiles)
    - name: public-security-group
      base:
        apiVersion: ec2.aws.upbound.io/v1beta1
        kind: SecurityGroup
        spec:
          forProvider:
            ingress:
              - fromPort: 443
                toPort: 443
                protocol: tcp
                cidrBlocks: ["0.0.0.0/0"]
```

**Declare your intent:**

```yaml
apiVersion: network.example.com/v1alpha1
kind: TubeLine
metadata:
  name: my-production-network
spec:
  lineName: "Production Northern Line"
  numberOfStations: 5
  publicAccess: true
  connectToAirport: true
```

Crossplane orchestrates building the entire line—tracks, stations, signals, turnstiles, and all.

## Signal Systems: Network Monitoring

The Tube’s signal system prevents crashes by monitoring train positions. In Crossplane Networking, you implement similar observability:

```yaml
# VPC Flow Logs (Train position tracking)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: FlowLog
metadata:
  name: tube-traffic-monitor
spec:
  forProvider:
    resourceIdRef:
      name: london-underground-vpc
    resourceType: VPC
    trafficType: ALL
    logDestinationType: cloud-watch-logs
    tags:
      Monitor: "Network Traffic Flow"
```

**What you can observe:**

- Which “trains” (packets) are traveling where
- Rejected connections at turnstiles (denied security group rules)
- Bottlenecks at transfer stations (routing issues)
- Unusual traffic patterns (security threats)

## The Night Tube: Multi-Region Networking

The Night Tube runs 24/7 on certain lines. For high availability, you run parallel networks across multiple regions (cities).

```yaml
# London Underground (eu-west-2)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPC
metadata:
  name: london-underground
spec:
  forProvider:
    cidrBlock: 10.1.0.0/16
    region: eu-west-2

---
# Manchester Metrolink (eu-west-1)
apiVersion: ec2.aws.upbound.io/v1beta1
kind: VPC
metadata:
  name: manchester-metrolink
spec:
  forProvider:
    cidrBlock: 10.2.0.0/16
    region: eu-west-1

---
# Inter-city connection via Transit Gateway
apiVersion: ec2.aws.upbound.io/v1beta1
kind: TransitGateway
metadata:
  name: national-rail-interconnect
spec:
  forProvider:
    description: "National rail network connecting regional metros"
    amazonSideAsn: 64512
```

**High availability pattern:**

- Primary: London Underground (eu-west-2)
- Failover: Manchester Metrolink (eu-west-1)
- Connection: Transit Gateway (National Rail)

If London experiences signal failure, Manchester handles the load.

## Putting It All Together: A Complete Journey

Let’s trace a passenger’s (HTTP request’s) journey through your Crossplane-managed Underground:

```
1. Passenger arrives at street level (Internet)
   ↓
2. Enters Northern Line station via turnstile (Internet Gateway + Security Group port 443)
   ↓
3. Boards train to King's Cross interchange (Load Balancer in public subnet)
   ↓
4. Transfers to Central Line platform (Route table directs to private subnet)
   ↓
5. Passes through Central Line turnstile (Security Group allows from load balancer)
   ↓
6. Arrives at application station (EC2 instance processes request)
   ↓
7. Takes staff corridor to Victoria Line (Security Group allows app → database)
   ↓
8. Accesses database station (RDS in deep private subnet)
   ↓
9. Returns via same route with response
   ↓
10. Exits to street level (Response through load balancer to internet)
```

**Declarative Crossplane Claim:**

```yaml
apiVersion: network.example.com/v1alpha1
kind: ThreeTierNetwork
metadata:
  name: my-web-application
spec:
  webTier:
    publicAccess: true
    allowedPorts: [80, 443]
  
  appTier:
    privateSubnet: true
    allowedSources: [webTier]
  
  dataTier:
    isolatedSubnet: true
    allowedSources: [appTier]
    backupEnabled: true
  
  monitoring:
    flowLogs: true
    vpcEndpoints: [s3, dynamodb]
```

Crossplane builds the entire Underground network from this simple declaration.

## Best Practices: Running a Reliable Tube Network

### 1. **Avoid Single Points of Failure (Don’t rely on one tunnel)**

```yaml
# Multi-AZ deployment
spec:
  subnets:
    - availabilityZone: eu-west-2a  # Tunnel under Zone A
    - availabilityZone: eu-west-2b  # Tunnel under Zone B
    - availabilityZone: eu-west-2c  # Tunnel under Zone C
```

### 2. **Implement Defense in Depth (Multiple security layers)**

```
Street → Station entrance → Ticket barrier → Platform gate → Train door
Internet → Internet Gateway → NACL → Security Group → Application firewall
```

### 3. **Monitor Everything (Signal control room)**

```yaml
resources:
  - VPC Flow Logs
  - CloudWatch Metrics
  - Transit Gateway Network Manager
  - VPC Reachability Analyzer
```

### 4. **Plan for Peak Hours (Capacity planning)**

```yaml
# Elastic Load Balancer = Platform that extends during rush hour
spec:
  scaling:
    minCapacity: 2
    maxCapacity: 10
    targetUtilization: 70
```

### 5. **Use Private Links (DLR-style dedicated services)**

```yaml
# Don't send passengers to street level just to reach another station
# Use VPC Endpoints for AWS services
vpcEndpoints:
  - s3
  - dynamodb
  - lambda
```

## Common Mistakes: Underground Disasters to Avoid

### ❌ **Allowing direct internet to private subnets**

```
DON'T: Victoria Line with direct exit to street
This is like putting an emergency exit in a deep tunnel without authorization
```

### ❌ **Overly permissive security groups**

```
DON'T: 0.0.0.0/0 allowed on all ports
This is like removing all turnstiles—anyone can board any train
```

### ❌ **Forgetting return routes**

```
DON'T: Inbound route configured but no return path
Passengers can enter but can't leave—station becomes dangerously overcrowded
```

### ❌ **Not using Network ACLs for critical subnets**

```
DON'T: Relying only on security groups for database tier
Add platform gates (NACLs) as a second layer of protection
```

### ❌ **Manual configuration drift**

```
DON'T: Manually adding routes or rules via AWS Console
Let Crossplane be the single source of truth (the official Tube map)
```

## Conclusion: Mind the Gap

Just as Transport for London doesn’t expect passengers to understand signal systems, track switches, and power distribution, Crossplane Networking lets you declare your network requirements without drowning in AWS networking complexity.

You declare:

```yaml
"I need a three-tier web application with public web servers, 
private application servers, and isolated databases"
```

Crossplane responds:

```
"I'll build you the Northern, Central, and Victoria lines with 
appropriate stations, transfers, turnstiles, and security. 
Please mind the gap."
```

Your infrastructure becomes a well-orchestrated transit system—secure, observable, and declarative.

**Next Steps:**

1. **Map your current network to Tube lines**: Identify which subnets are public (surface lines) vs private (deep tunnels)
1. **Implement security layers**: Add both turnstiles (security groups) and platform gates (NACLs)
1. **Create Compositions**: Build reusable network patterns like “standard three-tier” or “microservices mesh”
1. **Enable monitoring**: Install the signal system (VPC Flow Logs, CloudWatch)
1. **Practice GitOps**: Make your Tube map (network topology) version-controlled and declarative

Remember: **Good network design, like good public transport, is invisible when it works perfectly.** Passengers shouldn’t think about the complexity—they should just arrive at their destination safely and efficiently.

Now go build your Underground network. And please, mind the gap between your cloud resources.

-----

*What network metaphor would you like to see next? Let me know in the comments! 🚇*

**Tags:** #crossplane #kubernetes #networking #aws #infrastructure #devops #iac

-----

## Further Reading

- [Crossplane Documentation - Network Resources](https://docs.crossplane.io)
- [AWS VPC Best Practices](https://docs.aws.amazon.com/vpc/)
- [Crossplane Compositions Deep Dive](https://docs.crossplane.io/latest/concepts/compositions/)
- [Network Security: Defense in Depth](https://aws.amazon.com/architecture/security-identity-compliance/)

## About the Author

Willem van Heemstra is a Cloud Engineer specializing in Infrastructure-as-Code, Kubernetes, and Crossplane implementations. He believes complex technical concepts are best explained through creative metaphors that make learning faster and more enjoyable. Connect with him on [LinkedIn](#) or follow his articles on [Dev.to](#).

-----

*This article is part of a series explaining Crossplane concepts through everyday metaphors:*

- *Crossplane Basics: The Fast-Food Restaurant*
- *Crossplane Security: Defending Your Cyber-Vegetable Garden*
- *Crossplane with Crossview: The Monopoly Board Overview*
- *Crossplane E2E Testing: IKEA Furniture Assembly*
- *Crossplane Networking: Mind the Gap (You are here)*
