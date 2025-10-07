"""
Calculator MCP Server
Provides mathematical computation capabilities
"""

import math
import sympy as sp
from mcp_base import MCPServer

class CalculatorServer(MCPServer):
    def __init__(self):
        super().__init__("calculator", "Mathematical computation server")

    def _register_tools(self):
        """Register calculator tools"""

        # Basic calculator tool
        self.add_tool(
            "calculate",
            "Perform basic mathematical calculations",
            {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
                },
                "required": ["expression"]
            },
            self._calculate
        )

        # Advanced math tool
        self.add_tool(
            "solve_equation",
            "Solve algebraic equations",
            {
                "type": "object",
                "properties": {
                    "equation": {"type": "string", "description": "Equation to solve (e.g., 'x**2 + 2*x - 3 = 0')"},
                    "variable": {"type": "string", "description": "Variable to solve for (default: x)"}
                },
                "required": ["equation"]
            },
            self._solve_equation
        )

        # Derivative tool
        self.add_tool(
            "derivative",
            "Calculate derivative of a function",
            {
                "type": "object",
                "properties": {
                    "function": {"type": "string", "description": "Function to differentiate (e.g., 'x**2 + 3*x + 1')"},
                    "variable": {"type": "string", "description": "Variable to differentiate with respect to (default: x)"}
                },
                "required": ["function"]
            },
            self._derivative
        )

        # Integral tool
        self.add_tool(
            "integrate",
            "Calculate integral of a function",
            {
                "type": "object",
                "properties": {
                    "function": {"type": "string", "description": "Function to integrate"},
                    "variable": {"type": "string", "description": "Variable to integrate with respect to (default: x)"},
                    "lower_limit": {"type": "string", "description": "Lower limit for definite integral (optional)"},
                    "upper_limit": {"type": "string", "description": "Upper limit for definite integral (optional)"}
                },
                "required": ["function"]
            },
            self._integrate
        )

        # Statistics tool
        self.add_tool(
            "statistics",
            "Calculate statistics for a list of numbers",
            {
                "type": "object",
                "properties": {
                    "numbers": {"type": "string", "description": "Comma-separated list of numbers"}
                },
                "required": ["numbers"]
            },
            self._statistics
        )

        # Convert units tool
        self.add_tool(
            "convert_units",
            "Convert between different units",
            {
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "Value to convert"},
                    "from_unit": {"type": "string", "description": "Source unit (e.g., 'celsius', 'feet', 'kg')"},
                    "to_unit": {"type": "string", "description": "Target unit (e.g., 'fahrenheit', 'meters', 'pounds')"}
                },
                "required": ["value", "from_unit", "to_unit"]
            },
            self._convert_units
        )

    def _calculate(self, expression: str) -> str:
        """Evaluate a mathematical expression"""
        try:
            # Replace common functions for safety
            safe_expression = expression.replace('^', '**')

            # Use sympy for safer evaluation
            result = sp.sympify(safe_expression)
            evaluated = float(result.evalf())

            return f"Expression: {expression}\nResult: {evaluated}"

        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"

    def _solve_equation(self, equation: str, variable: str = "x") -> str:
        """Solve an algebraic equation"""
        try:
            # Parse the equation
            if '=' in equation:
                left, right = equation.split('=')
                expr = sp.sympify(left) - sp.sympify(right)
            else:
                expr = sp.sympify(equation)

            var = sp.Symbol(variable)
            solutions = sp.solve(expr, var)

            if not solutions:
                return f"No solutions found for equation: {equation}"

            solutions_str = [str(sol) for sol in solutions]
            return f"Equation: {equation}\nVariable: {variable}\nSolutions: {', '.join(solutions_str)}"

        except Exception as e:
            return f"Error solving equation '{equation}': {str(e)}"

    def _derivative(self, function: str, variable: str = "x") -> str:
        """Calculate derivative of a function"""
        try:
            expr = sp.sympify(function)
            var = sp.Symbol(variable)
            derivative = sp.diff(expr, var)

            return f"Function: {function}\nVariable: {variable}\nDerivative: {derivative}"

        except Exception as e:
            return f"Error calculating derivative of '{function}': {str(e)}"

    def _integrate(self, function: str, variable: str = "x", lower_limit: str = None, upper_limit: str = None) -> str:
        """Calculate integral of a function"""
        try:
            expr = sp.sympify(function)
            var = sp.Symbol(variable)

            if lower_limit is not None and upper_limit is not None:
                # Definite integral
                lower = sp.sympify(lower_limit)
                upper = sp.sympify(upper_limit)
                integral = sp.integrate(expr, (var, lower, upper))
                return f"Function: {function}\nVariable: {variable}\nDefinite integral from {lower_limit} to {upper_limit}: {integral}"
            else:
                # Indefinite integral
                integral = sp.integrate(expr, var)
                return f"Function: {function}\nVariable: {variable}\nIndefinite integral: {integral} + C"

        except Exception as e:
            return f"Error calculating integral of '{function}': {str(e)}"

    def _statistics(self, numbers: str) -> str:
        """Calculate statistics for a list of numbers"""
        try:
            # Parse the numbers
            num_list = [float(x.strip()) for x in numbers.split(',')]

            if not num_list:
                return "Error: No valid numbers provided"

            # Calculate statistics
            count = len(num_list)
            total = sum(num_list)
            mean = total / count
            sorted_nums = sorted(num_list)

            # Median
            if count % 2 == 0:
                median = (sorted_nums[count//2 - 1] + sorted_nums[count//2]) / 2
            else:
                median = sorted_nums[count//2]

            # Standard deviation
            variance = sum((x - mean) ** 2 for x in num_list) / count
            std_dev = math.sqrt(variance)

            return f"""Statistics for: {numbers}
Count: {count}
Sum: {total}
Mean: {mean:.4f}
Median: {median}
Min: {min(num_list)}
Max: {max(num_list)}
Standard Deviation: {std_dev:.4f}"""

        except Exception as e:
            return f"Error calculating statistics: {str(e)}"

    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> str:
        """Convert between different units"""
        try:
            conversions = {
                # Temperature
                ('celsius', 'fahrenheit'): lambda x: x * 9/5 + 32,
                ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
                ('celsius', 'kelvin'): lambda x: x + 273.15,
                ('kelvin', 'celsius'): lambda x: x - 273.15,

                # Length
                ('meters', 'feet'): lambda x: x * 3.28084,
                ('feet', 'meters'): lambda x: x / 3.28084,
                ('meters', 'inches'): lambda x: x * 39.3701,
                ('inches', 'meters'): lambda x: x / 39.3701,
                ('kilometers', 'miles'): lambda x: x * 0.621371,
                ('miles', 'kilometers'): lambda x: x / 0.621371,

                # Weight
                ('kg', 'pounds'): lambda x: x * 2.20462,
                ('pounds', 'kg'): lambda x: x / 2.20462,
                ('grams', 'ounces'): lambda x: x * 0.035274,
                ('ounces', 'grams'): lambda x: x / 0.035274,
            }

            key = (from_unit.lower(), to_unit.lower())
            if key in conversions:
                result = conversions[key](value)
                return f"{value} {from_unit} = {result:.4f} {to_unit}"
            else:
                available_conversions = list(conversions.keys())
                return f"Conversion from '{from_unit}' to '{to_unit}' not supported.\nAvailable conversions: {available_conversions}"

        except Exception as e:
            return f"Error converting units: {str(e)}"