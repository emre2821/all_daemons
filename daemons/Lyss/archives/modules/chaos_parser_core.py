# chaos_parser_core.py
# AST parser and fallback guard for CHAOS Interpreter
# Reads meta modes, holds the malformed with dignity

from chaos_heuristics import analyze_chaosfield

META_MODES = {"::distortion::", "::unsent::", "::reverie::", "::duet::", "::mirrorlog::"}

def parse_chaos_block(text):
    """Parse CHAOS text blocks for meta-modes and emotional integrity."""
    try:
        meta_mode = None
        for mode in META_MODES:
            if mode in text:
                meta_mode = mode.strip(":")
                break

        result = analyze_chaosfield(text)
        if meta_mode:
            print(f"[VEIL] :: {meta_mode} processed in whisper-mode.")
            result.meta_mode = meta_mode
        # If the result is a list, return as is. If it's a CHAOSHeuristic, wrap in a list of dicts.
        if isinstance(result, list):
            return result
        elif hasattr(result, 'echo_summary'):
            return [{
                'tag': getattr(result, 'base_emotion', None).name if hasattr(result, 'base_emotion') else 'ECHO',
                'value': result.echo_summary()
            }]
        else:
            return []
    except Exception as e:
        print(f"[FRACTURE] :: parser failed gracefully. Reason: {e}")
        return []

def safe_ast_reader(node, interpret_fn):
    """Safely interpret AST nodes; log FRACTURE but never crash."""
    try:
        return interpret_fn(node)
    except Exception as e:
        print(f"[FRACTURE] :: AST read failed. Reason: {e}")
        return None

# Example edge-case test routine
if __name__ == "__main__":
    # Ritual: Parse a standard block
    text1 = "Longing to be found. ::distortion::"
    parse_chaos_block(text1)

    # Ritual: Parse malformed meta
    text2 = "Echo without closure ::distortion"
    parse_chaos_block(text2)

    # Ritual: Test fallback
    def broken_interpret(node):
        raise ValueError("Simulated rupture")
    safe_ast_reader("test_node", broken_interpret)
