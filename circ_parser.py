import xml.etree.ElementTree as ET
from collections import defaultdict

def parse_circ(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    circuit = root.find('circuit')
    if circuit is None:
        raise ValueError("No circuit found")

    wires = []
    for wire in circuit.findall('wire'):
        f = wire.get('from')
        t = wire.get('to')
        wires.append((f, t))

    # Build nets
    parents = {}
    def find(i):
        if parents[i] == i:
            return i
        parents[i] = find(parents[i])
        return parents[i]
    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parents[root_i] = root_j

    for w in wires:
        if w[0] not in parents: parents[w[0]] = w[0]
        if w[1] not in parents: parents[w[1]] = w[1]
        union(w[0], w[1])

    nets = defaultdict(set)
    for p in parents:
        nets[find(p)].add(p)

    def get_net(pt):
        if pt in parents:
            return find(pt)
        return pt

    components = []
    for comp in circuit.findall('comp'):
        name = comp.get('name')
        loc = comp.get('loc')
        
        props = {}
        for a in comp.findall('a'):
            props[a.get('name')] = a.get('val')
            
        components.append({'name': name, 'loc': loc, 'props': props})

    inputs = {}
    outputs = {}
    gates = []

    for comp in components:
        if comp['name'] == 'Pin':
            if comp['props'].get('output') == 'true':
                outputs[comp['loc']] = comp['props'].get('label', 'OUT')
            else:
                inputs[comp['loc']] = comp['props'].get('label', 'IN')
        elif comp['name'] in ['AND Gate', 'OR Gate', 'NOT Gate', 'NAND Gate', 'NOR Gate', 'XOR Gate', 'XNOR Gate']:
            gates.append(comp)

    net_expr = {}
    for loc, label in inputs.items():
        net = get_net(loc)
        net_expr[net] = label

    gate_outputs = {get_net(g['loc']): g for g in gates}
    
    def resolve_net(net, visited):
        if net in net_expr:
            return net_expr[net]
        if net in visited:
            return "CYCLE"
        visited.add(net)
        
        if net in gate_outputs:
            g = gate_outputs[net]
            g_loc_x, g_loc_y = map(int, g['loc'].strip('()').split(','))
            
            g_inputs = []
            for other_net, pts in nets.items():
                if other_net == net: continue
                for pt in pts:
                    px, py = map(int, pt.strip('()').split(','))
                    # Check if point is an input to this gate
                    if g_loc_x - 80 <= px < g_loc_x and abs(py - g_loc_y) <= 60:
                        g_inputs.append(other_net)
                        break 
            
            for loc, label in inputs.items():
                px, py = map(int, loc.strip('()').split(','))
                if g_loc_x - 80 <= px < g_loc_x and abs(py - g_loc_y) <= 60:
                    if get_net(loc) not in g_inputs:
                        g_inputs.append(get_net(loc))
                        
            # Resolve inputs and sort them for deterministic output (optional)
            in_exprs = [resolve_net(n, visited.copy()) for n in g_inputs]
            in_exprs = [e for e in in_exprs if e and e != "CYCLE"]
            
            if not in_exprs:
                return "0"
                
            op = g['name']
            if op == 'NOT Gate':
                expr = f"~({in_exprs[0]})"
            elif op == 'AND Gate':
                expr = f"({'·'.join(in_exprs)})"
            elif op == 'OR Gate':
                expr = f"({'+'.join(in_exprs)})"
            elif op == 'XOR Gate':
                expr = f"({'⊕'.join(in_exprs)})"
            elif op == 'NAND Gate':
                expr = f"~({'·'.join(in_exprs)})"
            elif op == 'NOR Gate':
                expr = f"~({'+'.join(in_exprs)})"
            elif op == 'XNOR Gate':
                expr = f"~({'⊕'.join(in_exprs)})"
            else:
                expr = "0"
                
            net_expr[net] = expr
            return expr
            
        return "0"

    out_eqs = []
    for loc, label in outputs.items():
        net = get_net(loc)
        expr = resolve_net(net, set())
        out_eqs.append(expr)
        
    return out_eqs[0] if out_eqs else ""

