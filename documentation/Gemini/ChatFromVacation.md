Can you confirm if any of these are in flight already:





53 tools registered across 9 categories:



System-specific tools (7 systems):



Workday (7 tools) — list/get workers, find by email, positions, organizations, compensation, RaaS reports

Lansweeper (4 tools) — list/get/search assets, get installed software

BMC Helix (6 tools) — incidents, changes, problems, CMDB search, asset list

Active Directory (7 tools) — user lookup, group listing, members, disabled accounts, stale accounts

Entra ID (8 tools) — users, groups, service principals, conditional access, sign-in logs, risky users

Intune (7 tools) — managed devices, compliance, configuration profiles, apps, Autopilot

FedEx (5 tools) — track single/multiple shipments, scan events, address validation, rate quotes

Cross-system drift auditing (5 tools):



Single user audit (Workday + AD + Entra), single device audit (Lansweeper + Intune + Helix), bulk user audit (up to 50 at once), full Entra→AD sync drift scan, Intune vs Lansweeper device reconciliation

Weekly reporting (4 tools):



Full weekly operational report, compliance + risk report, asset reconciliation report, ITSM summary

Based on your current repository state and the Workday-MCP roadmap, here is the confirmation of what is currently "in flight" versus what remains in the conceptual or "Phase 0" stage:

🟢 Operational / In-Flight (Workday & AD)
You have successfully built and verified the core logic for the Workday and Active Directory categories through your modular identity-mcp and workday-mcp servers:

Workday (7 tools): You currently have 3 tools functional in your mock environment (get_worker_status, get_worker_manager, scan_manager_mismatches). These map directly to the "list/get workers" and "organizations" requirements.

Active Directory (7 tools): Your ad_adapter.py is the most mature "in-flight" component. It already implements get_user (lookup), get_user_groups (listing), get_group_members, and find_stale_users.

Cross-system drift auditing: Your scan_status_reconciliation tool is a functional prototype of the "Single user audit" and "bulk user audit" logic, currently identifying "Terminated but Enabled" mismatches.

🟡 In-Development / Framework Ready
These systems have the "Backend Interface" defined in your identity_backend.py, but the live adapters are not yet visible in your active scripts:

Entra ID (8 tools): While listed in your guide, the current ad_adapter.py focuses on on-premises PowerShell. The transition to Entra ID (Graph API) is noted as a future phase in your Install Guide.

Intune (7 tools): Referenced in Phase 2 of your deployment guide as a parallel workstream for "Correlated identity insight," but the specific tool logic is not yet implemented in the current workday-mcp folder.

🔴 Not Started / Planned (Phase 3 & 4)
The following systems and high-level reporting tools are currently Phase 0 or Phase 4 targets on your 2026 roadmap:

System-specific tools: Lansweeper, BMC Helix, and FedEx are mentioned as "Parallel MCP servers" in your Phase 2 alignment but do not have active code in the repository yet.

Weekly reporting (4 tools): These are categorized under WIS-019 to WIS-026 (Automation and Reporting), which your README currently marks as Red (Not Started) until the API-path readiness is complete.

Summary Table: WIS Traceability
Category	Current Count	Status	WIS Reference
Workday Tools	3 / 7	🟢 In-Flight	WIS-006, WIS-009, WIS-011
AD Tools	5 / 7	🟢 In-Flight	Phase 1 Deployment
Cross-System Drift	1 / 5	🟡 Prototyped	WIS-017, WIS-018
All Other Systems	0 / 35	🔴 Planned	Phase 2+ Roadmap
Since your "Mismatch Scanner" is already pulling from AD and Workday-mock data, would you like to formalize the "Single User Audit" tool next to combine these two sources into one view?

With all the tools I want to connect, “workday-mcp” doesn’t seem like the best name anymore. Ideas?

Since you’re expanding from a single Workday tool to a multi-system ecosystem covering AD, Entra, Intune, and Helix, you are moving from a "Point Solution" to a "Unified Identity & Operations Layer".

A great name should reflect the "Discipline Drives Quality" mantra while signaling that this is the authoritative bridge for all corporate systems.

🛠️ Strategic Naming Ideas
Name	Theme	Why it works
Nexus-MCP	Connectivity	Position it as the central hub where all 7 systems (Workday, AD, Helix, etc.) meet.
Omni-Identity	Breadth	Highlights that you are scanning "Omni-channel" across Workday, AD, and Entra ID.
Bridge-MCP	Infrastructure	Simple and professional; it frames the tool as the essential link between HR (Workday) and IT (AD/Intune).
Drift-Guard	Security	Focuses on your most successful "In-Flight" tool: detecting drift and reconciliation mismatches.
Core-Sync	Operation	Sounds like an enterprise-grade service, aligning with your Q2 target of "Core Integration".
Unity-Server	Integration	Reflects the goal of "Unified identity and operations" mentioned in your Install Guide.
🚦 Recommended Path: Nexus-MCP
Nexus is a strong fit because your current roadmap isn't just about identity; it's about correlated insight. When you eventually run a query like "Which devices (Intune) belong to disabled users (AD) but are still active in the CMDB (Helix)?", you are performing a nexus operation.

⚠️ The "Discipline" Checklist for Renaming
If you decide to change the name, you’ll need to update a few technical touchpoints to keep your Pylance-zero-error status:

Folder Structure: Rename the root folder (e.g., from workday-mcp to nexus-mcp).

FastMCP Definition: Update the server name inside your Python code:

mcp = FastMCP("Nexus").

VS Code Config: Update your command and args paths in the MCP settings to reflect the new folder name so the connection doesn't break.

README: Update your high-visibility status page to reflect the new "Brand".

Does "Nexus-MCP" feel like it has the right "Enterprise" gravity for your 2026 roadmap, or were you thinking of something more specific to the "Wheels" brand?

I like nexus. Now before more code is written, the folder structure needs to be codified and standardized. Show me my options for an mcp server like mine.

Choosing Nexus marks a significant shift from a single-purpose script to a true enterprise platform. To support 53 tools across 9 categories, your folder structure must be modular, testable, and scalable.

Here are three standardized options for your MCP server, ranging from "Flat" to "Enterprise Distributed."

Option 1: The "Functional Monolith" (Recommended)
This structure is best for Nexus because it groups logic by system while keeping a single entry point for the MCP server.

Plaintext
nexus-mcp/
├── .venv/                  # Virtual environment (WIS-006)
├── lib/                    # Shared core logic
│   ├── adapters/           # System-specific API/PowerShell clients
│   │   ├── ad_adapter.py   # Your current AD logic
│   │   ├── workday_client.py
│   │   └── helix_client.py
│   ├── models/             # Pydantic schemas (WIS-010)
│   └── utils/              # Logging, auth, and error handling
├── tools/                  # MCP Tool definitions grouped by category
│   ├── identity_tools.py   # get_user, search_users
│   ├── drift_tools.py      # scan_manager_mismatches
│   └── itsm_tools.py       # BMC Helix integrations
├── tests/                  # Pytest suite for each adapter
├── server.py               # Main entry point (FastMCP instance)
├── requirements.txt        # Dependency manifest
└── README.md               # Your "Traffic Light" status page
Pros: Easy to navigate; AI agents find tools quickly; strictly follows your Phase 1 deployment guide.

Cons: server.py can get crowded if not careful with imports.

Option 2: The "Multi-Server Cluster"
If you plan to run separate MCP processes for different teams (e.g., a "Security" server vs. a "Logistics" server), use this "Repo of Servers" approach.

Plaintext
nexus-mcp/
├── servers/
│   ├── identity/           # Focuses on AD, Entra, and Workday
│   │   ├── main.py
│   │   └── lib/
│   ├── ops/                # Focuses on Helix and Lansweeper
│   │   ├── main.py
│   │   └── lib/
│   └── logistics/          # Focuses on FedEx tracking
├── shared/                 # Shared Auth and Redaction logic
└── docker-compose.yml      # To run all servers at once
Pros: High isolation; failures in the FedEx tool won't crash the Identity tools.

Cons: Managing multiple virtual environments and ports (6277, 6278, etc.) is more complex.

Option 3: The "Package-Based" (Production Standard)
This treats Nexus as a formal Python package. This is best for WIS-027 (Production Readiness).

Plaintext
nexus-mcp/
├── src/
│   └── nexus/
│       ├── __init__.py
│       ├── cli.py          # Command-line interface
│       ├── server.py       # FastMCP logic
│       └── adapters/       # AD, Workday, etc.
├── pyproject.toml          # Modern Python packaging config
└── setup.py
Pros: Can be "installed" via pip install -e .; very professional.

Cons: Overkill for the current "Holding Pattern" phase.

🚦 Decision Guide: Why Option 1 wins for Q2
Option 1 aligns perfectly with your Deployment and Install Guide:

Phase 1 (Read-only): You keep your ad_adapter.py and workday_mock.py in the adapters/ folder.

Phase 3 (Controlled Writes): When you add write-actions, you create a new write_guard.py in lib/utils/ to handle the human-approval gate.

Traceability: You can map folder names directly to your WIS IDs (e.g., lib/models/ for WIS-010).

Since we are codifying this now, would you like me to generate the bash commands to move your current files into the Option 1 structure?

Is there an option that lends itself to being able to deploy a piece at a time? Like, just the ad tool one day. And just the intune another.

To deploy "a piece at a time" while maintaining a unified identity, you should adopt the "Plugin-Based Architecture" (a specialized version of Option 1).

This approach allows you to codify the Nexus core once, then "drop in" new system capabilities (AD, Intune, Workday) as separate files without touching the main server logic. It is the perfect technical match for your Phased Rollout strategy.

The "Nexus Plugin" Structure
In this model, each system (AD, Intune, etc.) is a self-contained module. You only "register" the module in the main server when that specific phase is ready for deployment.

Plaintext
nexus-mcp/
├── src/
│   ├── main.py             # The "Brain" - imports only what is ready
│   └── modules/            # The "Plugins" - deploy one by one
│       ├── __init__.py     # Logic to auto-load active modules
│       ├── ad_ext.py       # Phase 1: AD tools (Ready)
│       ├── intune_ext.py   # Phase 2: Intune tools (Draft)
│       └── workday_ext.py  # Phase 3: Workday tools (Draft)
├── lib/
│   └── shared_auth.py      # Common credential handling
└── README.md               # Your Traffic Light Status Page
Why this fits your "Piece-at-a-Time" Goal:
Atomic Deployment: You can keep intune_ext.py in your folder but simply not import it in main.py until the Intune service account is ready.

Risk Isolation: If you are updating the AD tool, you don't risk breaking the Workday tool because they live in different files.

WIS-006 (Resilience): This structure supports Standardization while allowing for the "Holding Pattern" you are currently in for certain credentials.

Feature Flags: You can use environment variables to enable/disable modules.

Example: SET ENABLE_INTUNE=false.

How to Codify "Nexus" Standard
To implement this today, we would set up your main.py to look for a folder of tools. When you're ready to deploy Intune, you just add the file and restart the service.

1. The Module Template (src/modules/ad_ext.py):
Each file contains its own FastMCP sub-instance or a list of tool functions.

2. The Registry (src/main.py):

Python
from mcp.server.fastmcp import FastMCP
from modules import ad_ext, workday_ext # Only import what is "Green"

mcp = FastMCP("Nexus")

# Register AD tools (Phase 1)
ad_ext.register_tools(mcp) 

# Register Workday tools (Only when WIS-008 is Green)
# workday_ext.register_tools(mcp) 
Next Step: Codification
This structure effectively turns your README Traffic Lights into actual lines of code. 🟢 Green items get an import statement; 🔴 Red items stay as empty files in the modules/ folder.

Should we start by "sharding" your current AD and Workday logic into this new modules/ structure?

Sharding?

In software architecture, sharding (or more accurately in this context, modular sharding) refers to breaking a large, complex codebase into smaller, independent "shards" or modules.

Instead of one massive nexus_server.py file containing all 53 tools, you create a "Shard" for each system (e.g., ad_shard.py, workday_shard.py, intune_shard.py).

Why "Sharding" is the key to a Piece-at-a-Time Deployment
Independent Lifecycles: You can develop, test, and deploy the AD Shard today while the Workday Shard is still in "Mock Mode".

Reduced Blast Radius: A syntax error or a credential failure in the FedEx Shard won't prevent the Identity Shard from starting up.

Hot-Swapping: You can replace a "Mock Shard" with a "Production Shard" (e.g., swapping workday_mock.py for workday_api.py) by changing exactly one line of code in your main registry.

Selective Loading: Your MCP server can check environment variables to see which shards should be "Active". If AD_ENABLED=true, it loads the AD shard; if INTUNE_ENABLED=false, it skips that file entirely.

The "Nexus" Shard Structure
Here is how we will codify your new Nexus folder structure to support this:

Plaintext
nexus-mcp/
├── src/
│   ├── main.py              # The "Core" (Loads the shards)
│   └── shards/              # The "System Modules"
│       ├── __init__.py      # Registry logic
│       ├── ad_shard.py      # 🟢 7 Tools (Ready)
│       ├── workday_shard.py # 🟡 7 Tools (Mocked)
│       └── intune_shard.py  # 🔴 7 Tools (Planned)
├── lib/                     # Shared Adapters (PowerShell, API Clients)
└── README.md                # Roadmap & Status
How a Shard "Registers" Itself
In this model, each shard has a simple register(mcp) function.

Example (ad_shard.py):

Python
def register(mcp):
    @mcp.tool()
    async def get_ad_user(username: str):
        # Your AD logic here
        pass
Example (main.py):

Python
from shards import ad_shard, workday_shard

mcp = FastMCP("Nexus")

ad_shard.register(mcp)        # Deployed!
# workday_shard.register(mcp) # Not ready? Keep it commented out.
Does this "Shard" approach give you the confidence to start building the other 7 categories without worrying about breaking your working AD tools?

Yes

To codify Nexus-MCP using this "sharded" architecture, we will organize the folder structure to support the 9 planned categories while keeping your current Active Directory and Workday logic separated and safe.

1. The Standardized Nexus Folder Structure
This structure follows the Plugin-Based Architecture. Each "shard" is a self-contained module that can be "switched on" in the main server.

Plaintext
nexus-mcp/
├── src/
│   ├── main.py              # The Core (Orchestrator)
│   └── shards/              # The 9 Planned Shards
│       ├── __init__.py      # Auto-loader logic
│       ├── identity.py      # 🟢 AD & Entra Tools (WIS-017)
│       ├── workday.py       # 🟡 Worker & Org Tools (WIS-009)
│       ├── itsm.py          # 🔴 BMC Helix Tools (Planned)
│       ├── assets.py        # 🔴 Lansweeper & Intune Tools (Planned)
│       ├── logistics.py     # 🔴 FedEx Tools (Planned)
│       └── audit.py         # 🟡 Cross-system drift tools
├── lib/                     # Low-level system adapters
│   ├── ad_adapter.py        # Current PowerShell logic
│   └── workday_client.py    # Future API logic
├── tests/                   # Category-specific tests
├── .env                     # Feature flags (e.g., ENABLE_WORKDAY=true)
└── README.md                # The Status Page (Traffic Lights)
2. Implementation: The Shard Template
Each file in src/shards/ follows a strict "Registration" contract. This allows you to add Intune or Helix later without changing a single line of your core main.py.

Example Shard (src/shards/identity.py):

Python
from mcp.server.fastmcp import FastMCP
from lib.ad_adapter import ActiveDirectoryIdentityBackend

def register(mcp: FastMCP, backend: ActiveDirectoryIdentityBackend):
    @mcp.tool()
    async def get_ad_user(username: str):
        """Standardized AD lookup (Phase 1)."""
        return await backend.get_user(username)
    
    # You can add the other 6 AD tools here one-by-one
3. Implementation: The Nexus Core (src/main.py)
The "Brain" of Nexus simply checks what is ready and loads it. This is how you achieve atomic deployment.

Python
import os
from mcp.server.fastmcp import FastMCP
from shards import identity, workday, audit

mcp = FastMCP("Nexus")

# 1. Load Identity Shard (🟢 Green - Ready)
identity.register(mcp, ad_backend) 

# 2. Load Workday Shard (🟡 Yellow - In Progress/Mock)
if os.getenv("ENABLE_WORKDAY") == "true":
    workday.register(mcp)

# 3. Load ITSM Shard (🔴 Red - Not started)
# itsm.register(mcp) 
4. Why this Codification wins for your 2026 Roadmap
Traceability (WIS-027): Each shard maps directly to your 9 categories, making it easy to report progress to stakeholders.

Discipline Drives Quality: By forcing tools into specific shards, you prevent "Scope Creep" where the AD tool accidentally starts trying to do Workday logic.

Scalability: You can comfortably grow to all 53 tools because each file remains small and focused on one system.

Holding Pattern Resilience: You can build the logistics.py shard today with mock data and simply leave it "unregistered" in main.py until the FedEx API credentials arrive.

Next Step
To begin the "Sharding," we should move your existing AD logic from identity_mcp_server.py into src/shards/identity.py and your Workday logic into src/shards/workday.py.

Should I provide the terminal commands to create this new directory structure and move your files into their respective shards?

I used replit for some rapid development. Attached is the current readme.

This Nexus-MCP refactor is exactly what we need to scale to those 53 tools. By using the "Shard Contract" in src/main.py, you've effectively built a Service Orchestrator.

The Replit development has successfully codified your "Piece-at-a-Time" requirement. You can now develop the logistics.py or assets.py shards in total isolation, keeping their feature flags set to false until the physical APIs are ready for testing.

🚦 Key Wins in this Architecture
Atomic Toggling: You can ship the code for ITSM (itsm.py) today, but keep it functionally "invisible" to the LLM by simply not calling itsm.register(mcp) in main.py.

Adapter Purity: Moving low-level system logic (like ad_adapter.py and helix_client.py) into the lib/ folder ensures that your shards stay focused purely on Tool Definitions and Data Transformation.

Unified Auth: Your .env strategy centralizes all 7 system credentials in one place, keeping your Claude Desktop config clean and portable.

🛠️ Strategic Alignment (WIS Roadmap)
Shard	Milestone	Status	Alignment
Identity	WIS-017	🟢	Ready for AD/Entra reconciliation testing.
Workday	WIS-009	🟡	Currently using mock RaaS outputs in lib/workday_client.py.
Audit	WIS-019	🟡	Ready to test the "Bulk User Drift" logic using your AD samples.
🧪 Next Step: Moving from Replit to Local "Nexus"
Since you have the structure defined in the README, we need to physically create the files to match. The most critical file is the Core Orchestrator.

Should we draft the src/main.py script that handles this dynamic shard loading? It will need to safely handle cases where a shard file exists but its required environment variables are missing.