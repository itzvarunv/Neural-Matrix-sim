import random
import json
import os
import math
import shutil

# =========================================================================
# ISOLATED SYSTEM STORAGE DIRECTORY SETUP
# =========================================================================
LOBBY_DIR = "regime_lobby"
CEMETERY_DIR = "regime_cemetery"
STATS_CSV = "regime_simulation_agent_data.csv"
MAX_YEARS = 100

def initialize_directories():
    for folder in [LOBBY_DIR, CEMETERY_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
    
    with open(STATS_CSV, "w") as f:
        f.write("Agent_ID,Gender,Total_Kids,Status,Cause_of_Death,Year_of_Death,Final_Savings,Final_Energy,Marital_Regime\n")

# =========================================================================
# INTERCONTINENTAL TRANSIT AUTHORITY (ITA)
# =========================================================================
class TransitAuthority:
    def __init__(self):
        self.fleet = {
            "Plane_Alpha": {"capacity": 15, "type": "Air", "interval": 3, "base": 60.0},
            "Plane_Beta":  {"capacity": 15, "type": "Air", "interval": 3, "base": 60.0},
            "Ship_Vanguard":{"capacity": 40, "type": "Sea", "interval": 5, "base": 25.0},
            "Ship_Freedom": {"capacity": 40, "type": "Sea", "interval": 5, "base": 25.0}
        }
        self.ledger = {}

    def get_dynamic_price(self, vehicle_id, year, current_bookings):
        v = self.fleet[vehicle_id]
        fill_ratio = current_bookings / v["capacity"]
        return v["base"] * (1.0 + fill_ratio)

    def issue_booking(self, year, vehicle_id, agent_id, overbook=False):
        if year not in self.ledger:
            self.ledger[year] = {vid: [] for vid in self.fleet.keys()}
        self.ledger[year][vehicle_id].append({"id": agent_id, "overbook": overbook})

ITA = TransitAuthority()

# =========================================================================
# NEURAL ENGINE MATRIX WITH PROPERTY REGIME OUTPUT
# =========================================================================
class NPCBrain:
    def __init__(self, weights=None):
        if weights is None:
            self.weights = [[random.uniform(-0.5, 0.5) for _ in range(8)] for _ in range(8)]
        else:
            self.weights = weights

    def forward(self, inputs):
        outputs = []
        for row in self.weights:
            val = sum(i * w for i, w in zip(inputs, row))
            outputs.append(math.tanh(val))
        return outputs

# =========================================================================
# NPC INDIVIDUAL COMPLEX LIFE CONSTRUCT
# =========================================================================
class BrainedCiv:
    def __init__(self, agent_id, gender, starting_savings=50.0):
        self.agent_id = agent_id
        self.gender = gender
        self.age = 18  
        self.energy = 90
        self.savings = starting_savings
        
        self.spouse = None
        self.marital_regime = "None"  
        self.children_produced = []
        
        self.status = "Alive"
        self.cause_of_death = "N/A"
        self.year_of_death = "N/A"
        
        self.active_ticket = None  
        self.brain = NPCBrain()
        self.biography = []

    def get_social_bracket(self):
        if self.savings > 150: return "Wealthy"
        if self.savings > 40:  return "Middle"
        return "Poor"

    def log_biography_snapshot(self, year, region):
        self.biography.append({
            "year": year, "age": self.age, "location_sector": region,
            "energy": self.energy, "savings_bank_balance": round(self.savings, 2),
            "social_class": self.get_social_bracket(), "marital_regime": self.marital_regime
        })

# =========================================================================
# DYNAMIC TRANSIT PROTOCOL WITH "FINAL CALL" CONFIRMATION
# =========================================================================
def process_boarding_and_transit(world_spaces, current_year):
    if current_year not in ITA.ledger: return world_spaces
        
    for region_name, space_dict in world_spaces.items():
        for vehicle_id, manifest in ITA.ledger[current_year].items():
            v_meta = ITA.fleet[vehicle_id]
            capacity = v_meta["capacity"]
            
            # 1. Gather all active local passengers who have a ticket for this run
            valid_queue = []
            for b in manifest:
                if b["id"] in space_dict:
                    npc = space_dict[b["id"]]
                    if npc.status == "Alive":
                        valid_queue.append(npc)

            confirmed_passengers = []
            
            # 2. RUN THE FINAL CALL CONFIRMATION PROTOCOL
            for npc in valid_queue:
                # If they are going bankrupt or dangerously sick, they reject the trip
                if npc.savings < 0.0 or npc.energy < 30:
                    # Apply your slight cash penalty for last-minute cancellation
                    cancellation_penalty = 5.0
                    npc.savings -= cancellation_penalty
                    npc.active_ticket = None  # Ticket discarded, slot freed up!
                else:
                    # They pass confirmation checks and join the boarding lineup
                    confirmed_passengers.append(npc)

            # 3. FILL SEATS WITH CONFIRMED PASSENGERS (Overbookers fill empty slots!)
            allowed = confirmed_passengers[:capacity]
            bumped = confirmed_passengers[capacity:]

            # Boarding execution loop
            for npc in allowed:
                # DEFENSIVE CHECK: If their ticket was cleared (e.g., already moved by a spouse), skip gracefully!
                if not npc.active_ticket:
                    continue
                    
                dest = npc.active_ticket["destination"]
                npc.energy -= 15  
                npc.active_ticket = None
                
                # Move agent file structures safely across regional tables
                del space_dict[npc.agent_id]
                world_spaces[dest][npc.agent_id] = npc
                
                # Spouse tags along safely
                if npc.spouse and npc.spouse.agent_id in space_dict:
                    spouse_npc = space_dict[npc.spouse.agent_id]
                    spouse_npc.energy -= 20
                    # Clear the spouse's ticket since they are traveling right now!
                    spouse_npc.active_ticket = None 
                    del space_dict[spouse_npc.agent_id]
                    world_spaces[dest][spouse_npc.agent_id] = spouse_npc

            # 4. INTEL_BUMP PROTECTION LOOP (No more death trap!)
            for npc in bumped:
                # Instead of stealing their cash/killing them, we push their ticket to next year
                npc.active_ticket["departure_year"] = current_year + 1
                ITA.issue_booking(current_year + 1, npc.active_ticket["vehicle"], npc.agent_id)
                npc.energy -= 5  # Minor terminal annoyance instead of fatal -35 fatigue!

    return world_spaces

# =========================================================================
# STAGGERED & RANDOMIZED NEURAL DIVORCE ENGINE (COMPUTE-OPTIMIZED)
# =========================================================================
def process_staggered_divorce(world_spaces, current_year):
    # 1. Gather all unique, active married couples across the entire world matrix
    all_couples = []
    evaluated_pairs = set()

    for region_name, space_dict in world_spaces.items():
        for npc in space_dict.values():
            if npc.status == "Alive" and npc.spouse:
                spouse_npc = npc.spouse
                if spouse_npc.status == "Alive" and spouse_npc.agent_id in space_dict:
                    pair_key = tuple(sorted([npc.agent_id, spouse_npc.agent_id]))
                    if pair_key not in evaluated_pairs:
                        evaluated_pairs.add(pair_key)
                        all_couples.append((npc, spouse_npc, space_dict))

    if not all_couples:
        return world_spaces

    # 2. SELECTION SHIFT: Process only a random subset (e.g., 25% of couples) this year
    # This prevents all divorces from executing on the same day and saves 75% compute!
    processing_ratio = 0.25 
    sample_size = max(1, int(len(all_couples) * processing_ratio))
    active_batch = random.sample(all_couples, sample_size)

    for npc, spouse_npc, space_dict in active_batch:
        # 3. RANDOM TIME-WINDOWING: Only evaluate if an agent passes a 2, 3, or 5-year check
        # This mirrors real-life relationship friction periods
        stagger_check = random.choice([2, 3, 5])
        if current_year % stagger_check != 0:
            continue  # The group shifts! This couple is skipped until their window aligns

        # Gather Neural Network Inputs
        local_density = len(space_dict)
        npc_inputs = [npc.energy, npc.savings, float(local_density), float(npc.age), spouse_npc.savings, spouse_npc.energy, float(len(npc.children_produced)), float(current_year)]
        spouse_inputs = [spouse_npc.energy, spouse_npc.savings, float(local_density), float(spouse_npc.age), npc.savings, npc.energy, float(len(spouse_npc.children_produced)), float(current_year)]
        
        # Read the Output Index 6 (Divorce Desire)
        npc_divorce_desire = npc.brain.forward(npc_inputs)[6]
        spouse_divorce_desire = spouse_npc.brain.forward(spouse_inputs)[6]

        # Neural friction threshold trigger
        if npc_divorce_desire > 0.45 or spouse_divorce_desire > 0.45:
            
            # --- ASSET LIQUIDITY REGIME RULES ---
            if npc.marital_regime == "Communist":
                # Splitting the shared pool equally
                total_pool = npc.savings + spouse_npc.savings
                npc.savings = total_pool / 2.0
                spouse_npc.savings = total_pool / 2.0
            
            # If 'Separate', they safely take exactly what they earned themselves.

            # Sever ties completely
            npc.spouse = None
            spouse_npc.spouse = None
            npc.marital_regime = "None"
            spouse_npc.marital_regime = "None"
            
            # Log the event natively to their biographies
            npc.biography.append({"year": current_year, "event": f"💔 Neural separation triggered. Left Agent {spouse_npc.agent_id}."})
            spouse_npc.biography.append({"year": current_year, "event": f"💔 Neural separation triggered. Left Agent {npc.agent_id}."})

    return world_spaces

# =========================================================================
# COURT-REGIME AND SEPARATION LOGIC
# =========================================================================
def process_procedural_courtship(world_spaces, current_year):
    for name, space_dict in world_spaces.items():
        females = [c for c in space_dict.values() if c.status == "Alive" and c.gender == "F" and not c.spouse]
        males = [c for c in space_dict.values() if c.status == "Alive" and c.gender == "M" and not c.spouse]
        
        random.shuffle(females)
        local_density = len(space_dict)

        for f in females:
            if not males: break
            suitor = random.choice(males)
            
            f_inputs = [f.energy, f.savings, float(local_density), float(f.age), suitor.savings, suitor.energy, float(len(f.children_produced)), float(current_year)]
            m_inputs = [suitor.energy, suitor.savings, float(local_density), float(suitor.age), f.savings, f.energy, float(len(suitor.children_produced)), float(current_year)]
            
            f_out = f.brain.forward(f_inputs)
            m_out = suitor.brain.forward(m_inputs)

            if f_out[1] > 0.15 and m_out[1] > 0.15:
                f_comm_lean = f_out[4] - f_out[5]
                m_comm_lean = m_out[4] - m_out[5]

                f.spouse = suitor
                suitor.spouse = f

                if f_comm_lean > 0.0 and m_comm_lean > 0.0:
                    f.marital_regime = "Communist"
                    suitor.marital_regime = "Communist"
                    pooled_savings = f.savings + suitor.savings
                    f.savings = pooled_savings / 2.0
                    suitor.savings = pooled_savings / 2.0
                else:
                    f.marital_regime = "Separate"
                    suitor.marital_regime = "Separate"

                males.remove(suitor)
    return world_spaces

# =========================================================================
# METABOLISM, LABOR MARKET, AND DEATH HANDLING
# =========================================================================
def process_metabolism_and_mortality(world_spaces, id_counter, current_year):
    for space_name, space_dict in world_spaces.items():
        newborns_to_add = []
        
        for uid, npc in list(space_dict.items()):
            if npc.status == "Dead": continue

            npc.age += 1
            npc.energy -= 6
            npc.savings -= 4.0  
            
            # --- THE LABOR ECONOMY ENGINE ---
            if npc.age >= 18 and npc.energy > 20:
                wages_earned = 12.0 * (npc.energy / 100.0)
                npc.savings += wages_earned
                npc.energy -= 4  # Labor expenditure cost
            
            # Travel booking pipeline
            if not npc.active_ticket and npc.age >= 18:
                local_density = len(space_dict)
                inputs = [npc.energy, npc.savings, float(local_density), float(npc.age), 0.0, 0.0, float(len(npc.children_produced)), float(current_year)]
                move_desire = npc.brain.forward(inputs)[0]
                
                if move_desire > 0.40:
                    chosen_v = random.choice(["Plane_Alpha", "Ship_Vanguard"])
                    existing_bookings = len(ITA.ledger.get(current_year+2, {}).get(chosen_v, []))
                    cost = ITA.get_dynamic_price(chosen_v, current_year+2, existing_bookings)
                    
                    if npc.savings >= cost:
                        npc.savings -= cost
                        destinations = [r for r in world_spaces.keys() if r != space_name]
                        npc.active_ticket = {"vehicle": chosen_v, "destination": random.choice(destinations), "departure_year": current_year+2}
                        ITA.issue_booking(current_year+2, chosen_v, npc.agent_id)

            # Repopulation Handler
            if npc.gender == "F" and npc.spouse and npc.spouse.agent_id in space_dict:
                husband = space_dict[npc.spouse.agent_id]
                if husband.status == "Alive":
                    f_inputs = [npc.energy, npc.savings, float(len(space_dict)), float(npc.age), husband.savings, husband.energy, float(len(npc.children_produced)), float(current_year)]
                    if npc.brain.forward(f_inputs)[7] > 0.30:
                        maternal_tax = 25.0
                        can_afford = False
                        
                        if npc.marital_regime == "Communist" and (npc.savings + husband.savings) > maternal_tax:
                            can_afford = True
                        elif npc.marital_regime == "Separate" and npc.savings > 12.5 and husband.savings > 12.5:
                            can_afford = True
                        
                        if can_afford:
                            npc.savings -= maternal_tax / 2
                            husband.savings -= maternal_tax / 2
                            npc.energy -= 15
                            
                            id_counter += 1
                            child_gender = "M" if random.random() < 0.50 else "F"
                            child_npc = BrainedCiv(id_counter, child_gender, starting_savings=maternal_tax)
                            child_npc.age = 0
                            
                            newborns_to_add.append(child_npc)
                            npc.children_produced.append(id_counter)
                            husband.children_produced.append(id_counter)

            # Health recovery purchases
            if npc.savings >= 12.0 and npc.energy <= 40:
                npc.savings -= 12.0
                npc.energy += 35

            # Mortality Checks
            if npc.energy <= 0 or npc.savings < -20.0:
                npc.status = "Dead"
                npc.cause_of_death = "Starvation / Exhaustion"
                npc.year_of_death = current_year
                if npc.spouse and npc.spouse.status == "Alive":
                    npc.spouse.marital_regime = "None"
                export_agent_metrics(npc)
                del space_dict[uid]
                
            elif npc.age >= random.randint(75, 90):
                npc.status = "Dead"
                npc.cause_of_death = "Biological Limit (Old Age)"
                npc.year_of_death = current_year
                if npc.spouse and npc.spouse.status == "Alive":
                    npc.spouse.marital_regime = "None"
                export_agent_metrics(npc)
                del space_dict[uid]

        for baby in newborns_to_add:
            space_dict[baby.agent_id] = baby
                
    return world_spaces, id_counter

# =========================================================================
# DATA EXPORT SYSTEM
# =========================================================================
def export_agent_metrics(npc):
    folder = LOBBY_DIR if npc.status == "Alive" else CEMETERY_DIR
    filepath = os.path.join(folder, f"ai_{npc.agent_id}_report.json")
    
    payload = {
        "agent_id": npc.agent_id, "gender": npc.gender, "final_status": npc.status,
        "marital_regime": npc.marital_regime, "cause_of_death": npc.cause_of_death,
        "year_of_death": npc.year_of_death, "final_savings": round(npc.savings, 2),
        "history": npc.biography
    }
    with open(filepath, "w") as f:
        json.dump(payload, f, indent=4)
        
    with open(STATS_CSV, "a") as f:
        f.write(f"{npc.agent_id},{npc.gender},{len(npc.children_produced)},{npc.status},"
                f"{npc.cause_of_death},{npc.year_of_death},{round(npc.savings, 2)},"
                f"{npc.energy},{npc.marital_regime}\n")

# =========================================================================
# CORE EXECUTION LOOP
# =========================================================================
def execute_matrix_loop():
    initialize_directories()
    world_spaces = {"Europe": {}, "Asia": {}, "Africa": {}}
    id_counter = 1
    
    for region in world_spaces.keys():
        for _ in range(40):
            gender = "F" if id_counter % 2 == 0 else "M"
            init_cash = random.uniform(20.0, 180.0)
            world_spaces[region][id_counter] = BrainedCiv(id_counter, gender, starting_savings=init_cash)
            id_counter += 1

    print("="*95)
    print("   RUNNING TRANSIT PROTOCOL MATRICES: LIVE JOBS WITH LAST-SECOND CONFIRMATION FARES")
    print("="*95)

    for year in range(1, MAX_YEARS + 1):
        total_alive = sum(len([c for c in space.values() if c.status == "Alive"]) for space in world_spaces.values())
        if total_alive == 0:
            print(f"[YEAR {year:02d}] ☠️ MATRIX COLLAPSED: TOTAL SYSTEM EXTINCTION.")
            break
            
        for name, space in world_spaces.items():
            for npc in space.values():
                npc.log_biography_snapshot(year, name)
                
        # Pipe execution segments
        world_spaces = process_boarding_and_transit(world_spaces, year)
        world_spaces = process_procedural_courtship(world_spaces, year)
        world_spaces = process_staggered_divorce(world_spaces, year)
        world_spaces, id_counter = process_metabolism_and_mortality(world_spaces, id_counter, year)
        
        all_npcs = [n for space in world_spaces.values() for n in space.values() if n.status == "Alive"]
        comm_cnt = len([n for n in all_npcs if n.marital_regime == "Communist"])
        sep_cnt = len([n for n in all_npcs if n.marital_regime == "Separate"])
        
        eu_pop = len(world_spaces["Europe"])
        as_pop = len(world_spaces["Asia"])
        af_pop = len(world_spaces["Africa"])
        
        print(f"[YEAR {year:02d}] Pop: {total_alive:<4} | Comm: {comm_cnt:<3} | Sep: {sep_cnt:<3} | Sectors (EU/AS/AF): {eu_pop}/{as_pop}/{af_pop}")

    for space in world_spaces.values():
        for npc in space.values():
            if npc.status == "Alive":
                export_agent_metrics(npc)

if __name__ == "__main__":
    execute_matrix_loop()
