from intbase import InterpreterBase
from intbase import ErrorType
from brewparse import parse_program

class Interpreter(InterpreterBase):

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor
        self.variable_name_to_value = {}
        self.trace_output = trace_output


    def interpret_statement(self, statement):
        if self.trace_output == True:
    	    print(statement) 

    # Citation: I used the pseudocode found on page 8 of CS131 Fall 25 Project #1 (Public) document. It was super helpful.

    def run(self, program):
        ast = parse_program(program)
        main_func_node = self.get_main_func_node(ast)
        # self.interpret_statement(main_func_node)
        self.run_func(main_func_node)

    def get_main_func_node(self, head_node):
        if head_node.elem_type == "program":
            functions = head_node.get("functions")
            # If find main under program then return it
            for function in functions:
                if function.get("name") == "main":
                    return function
            # Otherwise return name error
            super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )
    
    def run_func(self, func_node):
        for statement_node in func_node.get("statements"):
            self.run_statement(statement_node)
    
    def run_statement(self, statement_node):
        if self.is_definition(statement_node):
            self.do_definition(statement_node)
        elif self.is_assignment(statement_node):
            self.do_assignment(statement_node)
        elif self.is_func_call(statement_node):
            self.do_func_call(statement_node)
            return
    
    def is_definition(self, statement_node):
        if statement_node.elem_type == "vardef":
            return True
        else:
            return False
    
    def is_assignment(self, statement_node):
        if statement_node.elem_type == "=":
            return True
        else:
            return False
    
    def is_func_call(self, statement_node):
        if statement_node.elem_type == "fcall":
            return True
        else:
            return False

    def do_definition(self, statement_node):
        var_name = statement_node.get("name")
        # self.interpret_statement(var_name)
        if var_name in self.variable_name_to_value:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} defined more than once",
            )
        self.variable_name_to_value[var_name] = None

    def do_assignment(self, statement_node):
        target_var_name = statement_node.get("var")
        if target_var_name not in self.variable_name_to_value:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {target_var_name} has not been defined",
            )
        self.interpret_statement(statement_node)
        source_node = self.get_expression_node(statement_node)
        self.interpret_statement(source_node)
        resulting_value = self.evaluate_expression(source_node)
        self.variable_name_to_value[target_var_name] = resulting_value
        self.interpret_statement(resulting_value)
    
    def get_expression_node(self, statement_node):
        return statement_node.get("expression")

    # post order dfs
    def evaluate_expression(self, expression_node):

        # Base cases
        if expression_node is None:
            return None

        # psot order dfs
        left = self.evaluate_expression(expression_node.get("op1"))
        right = self.evaluate_expression(expression_node.get("op2"))

        if self.is_value_node(expression_node):
            return self.get_value(expression_node)
        elif self.is_variable_node(expression_node):
            return self.get_value_of_variable(expression_node)
        elif self.is_binary_operator(expression_node):
            return self.evaluate_binary_operator(expression_node, left, right)
        elif self.is_inputi(expression_node):
            return self.do_inputi_call(expression_node.get("args"))

    
    def is_value_node(self, expression_node):
        if expression_node.elem_type == "int" or expression_node.elem_type == "string":
            return True
        else:
            return False
    
    def get_value(self, expression_node):
        return expression_node.get("val")
    
    def is_variable_node(self, expression_node):
        if expression_node.elem_type == "qname":
            return True
        else:
            return False
    
    def get_value_of_variable(self, expression_node):
        value_variable = expression_node.get("name")
        if value_variable in self.variable_name_to_value:
            if self.variable_name_to_value[value_variable] != None:
                return self.variable_name_to_value[value_variable]
            else:
                super().error(
                    ErrorType.FAULT_ERROR,
                    f"Variable {value_variable} has not been initialized",
                )
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {value_variable} has not been defined",
            )
    
    def is_binary_operator(self, expression_node):
        if expression_node.elem_type == "+" or expression_node.elem_type == "-":
            return True
        else:
            return False
    
    def evaluate_binary_operator(self, expression_node, left, right):
        if type(left) != int or type(right) != int:
            super().error(
                ErrorType.TYPE_ERROR,
                f"Either variables {left} or {right} are not ints",
            )
        binary_operator = expression_node.elem_type
        if binary_operator == "+":
            return left + right
        else:
            return left - right
    
    def do_func_call(self, expression_node):
        func_call = expression_node.get("name")
        args = expression_node.get("args")
        if (func_call == "print"):
            self.do_print_call(args)
        elif (func_call == "inputi"):
            self.do_inputi_call(args)
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Function {func_call} has not been defined",
            )
    
    def do_print_call(self, args):
        string_to_output = ""
        if args != None:
            for arg in args:
                expr = self.evaluate_expression(arg)
                string_to_output += str(expr)
        super().output(string_to_output)

    def is_inputi(self, expression_node):
        if (expression_node.elem_type == "fcall" and expression_node.get("name") == "inputi"):
            return True
        else:
            return False
    
    def do_inputi_call(self, args):
        if args != None:
            if len(args) > 1:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"No inputi() function found that takes > 1 parameter",
                )
            elif len(args) == 1:
                prompt = args[0].get("val")
                super().output(prompt)
        user_input = super().get_input()
        return int(user_input)

# program = """def main() {
#              var foo;
#              var bar;
#              bar = 4 + inputi("enter a number: ") + inputi();
#              foo = 5;
#              print("The sum is: ", foo - (bar + 2));
#           }"""

# interpreter = Interpreter()
# interpreter.run(program)   
        

"""
	def run_func(func_node):
		for each statement_node in func_node.statements:
			run_statement(statement_node)

	def run_statement(statement_node):
            if is_definition(statement_node):
			do_definition(statement_node);
		else if is_assignment(statement_node):
			do_assignment(statement_node);
		else if is_func_call(statement_node):
			do_func_call(statement_node);
		...


      ...        

	def do_assignment(statement_node):
		target_var_name = get_target_variable_name(statement_node)
            if !var_name_exists(target_var_name):
                generate_error("Undefined variable " + target_var_name)
		source_node = get_expression_node(statement_node)
		resulting_value = evaluate_expression(source_node)
		this.variable_name_to_value[target_var_name] = resulting_value
     
      def evaluate_expression(expression_node):
            if is_value_node(expression_node):
                return get_value(expression_node)
            else if is_variable_node(expression_node):
                return get_value_of_variable(expression_node)
            else if is_binary_operator(expression_node):
                return evaluate_binary_operator(expression_node)
            ...
	...
"""      

