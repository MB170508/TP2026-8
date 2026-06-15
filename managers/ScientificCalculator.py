import math
import re
import ast
import operator

class ScientificCalculator:
    def __init__(self):
        self.history = []
        self.available_functions = {
            # Trigonometric
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
            # Exponential and logarithmic
            'exp': math.exp, 'log': math.log, 'log10': math.log10, 'log2': math.log2,
            'sqrt': math.sqrt, 'pow': math.pow,
            # Constants
            'pi': math.pi, 'e': math.e,
            # Other
            'abs': abs, 'round': round, 'ceil': math.ceil, 'floor': math.floor,
            'factorial': math.factorial, 'gamma': math.gamma,
        }
        self.examples = [
            "sin(pi/2)",
            "sqrt(16) + log10(100)",
            "2**3 + factorial(5)",
            "cos(0) * exp(1)",
            "pi * r**2",  # Note: r would need to be defined
        ]

    def evaluate_expression(self, expression: str) -> dict:
        """Evaluate a mathematical expression safely."""
        if not expression.strip():
            return {"success": False, "message": "Expression cannot be empty."}

        try:
            # Replace ^ with ** for exponentiation
            expr = expression.replace('^', '**')

            # Create a safe evaluation environment
            safe_dict = {
                '__builtins__': {},
                **self.available_functions
            }

            # Parse and evaluate
            result = eval(expr, safe_dict)

            # Store in history
            self.history.append({
                "expression": expression,
                "result": result
            })

            return {
                "success": True,
                "result": result,
                "message": f"Result: {result}"
            }

        except ZeroDivisionError:
            return {"success": False, "message": "Division by zero."}
        except NameError as e:
            return {"success": False, "message": f"Undefined variable or function: {str(e)}"}
        except (ValueError, TypeError) as e:
            return {"success": False, "message": f"Invalid operation: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Error evaluating expression: {str(e)}"}

    def get_available_functions(self) -> dict:
        """Return list of available functions."""
        return {
            "success": True,
            "functions": list(self.available_functions.keys()),
            "message": f"Available functions: {', '.join(self.available_functions.keys())}"
        }

    def get_examples(self) -> dict:
        """Return example expressions."""
        return {
            "success": True,
            "examples": self.examples,
            "message": "Example expressions loaded."
        }

    def get_history(self) -> dict:
        """Return calculation history."""
        return {
            "success": True,
            "history": self.history[-10:],  # Last 10 entries
            "message": f"History: {len(self.history)} entries"
        }

    def clear_history(self) -> dict:
        """Clear calculation history."""
        self.history.clear()
        return {
            "success": True,
            "message": "History cleared."
        }


# Legacy functions for backward compatibility
def evaluate_expression(expression: str) -> dict:
    calc = ScientificCalculator()
    return calc.evaluate_expression(expression)

def get_available_functions() -> dict:
    calc = ScientificCalculator()
    return calc.get_available_functions()

def get_examples() -> dict:
    calc = ScientificCalculator()
    return calc.get_examples()