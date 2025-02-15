import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        
        for variable in self.crossword.variables:
            new_domain_words = self.domains[variable].copy()
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    new_domain_words.remove(word)
            
            self.domains[variable] = new_domain_words.copy()

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        revise = False
        
        if overlap == None:
            return False
        
        x_index = overlap[0]
        y_index = overlap[1]
        
        words_to_remove = []
        for word_x in self.domains[x]:
            has_possibility = False
            for word_y in self.domains[y]:
                if word_x != word_y and word_x[x_index] == word_y[y_index]:
                    has_possibility = True
                    break
            
            if not has_possibility:
                words_to_remove.append(word_x)
                revise = True
        
        for word in words_to_remove:
            self.domains[x].remove(word)
        
        return revise
                
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.variables:
                    if x != y:
                        arcs.append((x, y))
        
        while arcs:
            arc = arcs.pop()
            x = arc[0]
            y = arc[1]
            
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        arcs.append((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """        
        for var in self.crossword.variables:
            if var not in assignment or not assignment[var]:
                return False
        return True
        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var, word in assignment.items():
            if word not in self.domains[var]:
                return False
            
            # unary
            if len(word) != var.length:
                return False

            # binary
            for other_var, other_word in assignment.items():
                if var == other_var:
                    continue
                overlap = self.crossword.overlaps[var, other_var]
                if overlap:
                    i, j = overlap
                    if word[i] != other_word[j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        values = {}

        for word in self.domains[var]:
            ruled_out = 0
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                for neighbor_word in self.domains[neighbor]:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if overlap:
                        i, j = overlap
                        if word[i] != neighbor_word[j]:
                            ruled_out += 1
            values[word] = ruled_out

        sorted_values = sorted(values, key=values.get)
        return sorted_values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        selected_var = None, sys.maxsize
        
        for var in self.crossword.variables:
            if var in assignment:
                continue
            domain_value = len(self.domains[var])
            
            if domain_value < selected_var[1]:
                selected_var = var, domain_value
            
            elif domain_value == selected_var[1]:
                var_neighbor_count = len(self.crossword.neighbors(var))
                selected_var_neighbor_count = len(self.crossword.neighbors(selected_var[0]))
                
                if var_neighbor_count > selected_var_neighbor_count:
                    selected_var = var, domain_value

        return selected_var[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            
            if self.consistent(assignment):
                
                domains_copy = {v: self.domains[v].copy() for v in self.domains}
            
                arcs = [(neighbor, var) for neighbor in self.crossword.neighbors(var)]
                if self.ac3(arcs):
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result

                # Restore the domains if AC-3 fails
                self.domains = domains_copy   
                assignment.pop(var)
            
        return None
                
            
def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
