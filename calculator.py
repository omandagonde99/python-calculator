"""
Premium Desktop Calculator
A sleek, modern, and beautiful standard/scientific calculator built with pure Python and Tkinter.
Features:
  - Responsive layout with standard and scientific modes.
  - Collapsible history panel with selectable equations.
  - Custom glassmorphism-inspired canvas buttons with hover/press animations.
  - Safe math AST parser (no direct eval).
  - High-DPI screen awareness on Windows.
  - Interactive keyboard shortcuts.
"""

import sys
import tkinter as tk
import math
import ast
import operator

# Set High-DPI Awareness on Windows to ensure razor-sharp graphics and text
try:
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class SafeMathEvaluator:
    """Safe mathematical expression parser and evaluator using AST."""
    def __init__(self, controller):
        self.controller = controller
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
            ast.Mod: operator.mod,
        }
        self.functions = {
            'sin': self._sin,
            'cos': self._cos,
            'tan': self._tan,
            'log': math.log10,
            'ln': math.log,
            'sqrt': math.sqrt,
            'exp': math.exp,
            'fact': self._factorial,
            'abs': abs,
        }
        self.constants = {
            'pi': math.pi,
            'e': math.e,
        }

    def _sin(self, x):
        if self.controller.is_degrees:
            return math.sin(math.radians(x))
        return math.sin(x)

    def _cos(self, x):
        if self.controller.is_degrees:
            return math.cos(math.radians(x))
        return math.cos(x)

    def _tan(self, x):
        if self.controller.is_degrees:
            # Check for tan(90) or tan(270) etc. in degree mode
            if self.controller.is_degrees and (round(x) - 90) % 180 == 0:
                raise ValueError("Math Error")
            return math.tan(math.radians(x))
        return math.tan(x)

    def _factorial(self, x):
        if x < 0 or not float(x).is_integer():
            raise ValueError("Math Error")
        if x > 1000:  # Prevent huge computation hanging
            raise ValueError("Overflow")
        return math.factorial(int(x))

    def evaluate(self, expr_str):
        # Format visual signs to Python standard syntax
        expr = expr_str.replace('×', '*').replace('÷', '/').replace('^', '**')
        # Support basic implicit multiplication (e.g. 2pi -> 2*pi, 2( -> 2*( )
        # To keep it simple, we let the safe evaluator parse clean syntax.
        
        try:
            tree = ast.parse(expr, mode='eval')
            result = self._eval_node(tree.body)
            
            if isinstance(result, complex):
                raise ValueError("Real numbers only")
                
            if isinstance(result, float):
                if result.is_integer():
                    return int(result)
                # Round to prevent float inaccuracies like 0.1 + 0.2 = 0.30000000000000004
                result = round(result, 14)
                # Truncate very tiny floats close to 0 to zero
                if abs(result) < 1e-14:
                    return 0
            return result
        except ZeroDivisionError:
            raise ZeroDivisionError("Division by Zero")
        except OverflowError:
            raise OverflowError("Result Overflow")
        except Exception as e:
            if "Math Error" in str(e) or "Overflow" in str(e):
                raise e
            raise ValueError("Syntax Error")

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif hasattr(ast, 'Num') and isinstance(node, getattr(ast, 'Num')):
            return node.n
        elif hasattr(ast, 'Str') and isinstance(node, getattr(ast, 'Str')):
            return node.s
        elif isinstance(node, ast.Name):
            if node.id in self.constants:
                return self.constants[node.id]
            raise ValueError(f"Unknown constant: {node.id}")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self.operators:
                # Prevent power hang (e.g., 99999^99999)
                if op_type == ast.Pow and left > 1000 and right > 1000:
                    raise ValueError("Overflow")
                return self.operators[op_type](left, right)
            raise ValueError("Unsupported Operator")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self.operators:
                return self.operators[op_type](operand)
            raise ValueError("Unsupported Unary")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.functions:
                args = [self._eval_node(arg) for arg in node.args]
                return self.functions[node.func.id](*args)
            raise ValueError("Unsupported Function")
        raise ValueError("Invalid Syntax")


class ModernButton(tk.Canvas):
    """Custom canvas-rendered rounded button with hover and active animations."""
    def __init__(self, parent, text, command, bg_color, hover_color, pressed_color, text_color, font, radius=12, **kwargs):
        super().__init__(parent, bd=0, highlightthickness=0, bg=parent["bg"], **kwargs)
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.text_color = text_color
        self.font = font
        self.radius = radius

        self.current_bg = self.bg_color
        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        
        # Capping radius to fit button size
        r = min(self.radius, w // 2, h // 2)
        r = max(r, 0)
        
        # Drawing standard rounded rect using overlapping rectangles and ovals
        if r > 0:
            # 4 Corners
            self.create_oval(0, 0, 2*r, 2*r, fill=self.current_bg, outline=self.current_bg, width=0)
            self.create_oval(w - 2*r, 0, w, 2*r, fill=self.current_bg, outline=self.current_bg, width=0)
            self.create_oval(0, h - 2*r, 2*r, h, fill=self.current_bg, outline=self.current_bg, width=0)
            self.create_oval(w - 2*r, h - 2*r, w, h, fill=self.current_bg, outline=self.current_bg, width=0)
            # Overlapping middle rects
            self.create_rectangle(r, 0, w - r, h, fill=self.current_bg, outline=self.current_bg, width=0)
            self.create_rectangle(0, r, w, h - r, fill=self.current_bg, outline=self.current_bg, width=0)
        else:
            self.create_rectangle(0, 0, w, h, fill=self.current_bg, outline=self.current_bg, width=0)
            
        # Draw central text
        self.create_text(w // 2, h // 2, text=self.text, fill=self.text_color, font=self.font, tags="text")

    def _on_enter(self, event):
        self.current_bg = self.hover_color
        self._draw()

    def _on_leave(self, event):
        self.current_bg = self.bg_color
        self._draw()

    def _on_press(self, event=None):
        self.current_bg = self.pressed_color
        self._draw()

    def _on_release(self, event=None):
        self.current_bg = self.hover_color
        self._draw()
        if self.command:
            self.command()

    def flash(self):
        """Simulate button press programmatically (for keyboard shortcut responses)."""
        self.current_bg = self.pressed_color
        self._draw()
        # Revert back to normal background after 100ms
        self.after(100, self._restore_normal)
        if self.command:
            self.command()

    def _restore_normal(self):
        self.current_bg = self.bg_color
        self._draw()


class ScrollableHistoryFrame(tk.Frame):
    """Modern scrollable frame for calculation history."""
    def __init__(self, parent, select_callback, bg_color, **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        self.select_callback = select_callback
        self.bg_color = bg_color

        self.canvas = tk.Canvas(self, bg=self.bg_color, bd=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, width=8)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Smart mousewheel scrolling (only when mouse is inside history frame)
        self.scrollable_frame.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.scrollable_frame.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def add_history_item(self, equation, result):
        # Create a container frame for the card
        card = tk.Frame(self.scrollable_frame, bg="#16161A", bd=0, relief="flat", padx=10, pady=8)
        card.pack(fill="x", padx=10, pady=6)

        # Truncate displays for layout fit
        eq_disp = equation if len(equation) < 26 else equation[:23] + "..."
        res_disp = str(result) if len(str(result)) < 16 else str(result)[:13] + "..."

        eq_lbl = tk.Label(card, text=eq_disp, bg="#16161A", fg="#80808C", font=("Segoe UI", 10), anchor="w")
        eq_lbl.pack(fill="x")

        res_lbl = tk.Label(card, text="= " + res_disp, bg="#16161A", fg="#7C4DFF", font=("Segoe UI", 12, "bold"), anchor="w")
        res_lbl.pack(fill="x")

        # Visual highlights on hover
        def on_enter(e):
            card.config(bg="#1E1E24")
            eq_lbl.config(bg="#1E1E24")
            res_lbl.config(bg="#1E1E24")

        def on_leave(e):
            card.config(bg="#16161A")
            eq_lbl.config(bg="#16161A")
            res_lbl.config(bg="#16161A")

        def on_click(e):
            self.select_callback(equation, result)

        for widget in (card, eq_lbl, res_lbl):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()


class CalculatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculator")
        self.root.geometry("400x650")
        self.root.minsize(360, 600)
        self.root.configure(bg="#0F0F12")

        # Calculator Model Variables
        self.expression = ""
        self.result_shown = False
        self.is_degrees = True
        self.scientific_active = False
        self.history_active = False
        self.history_items = []  # Tuples of (expression, result)

        self.evaluator = SafeMathEvaluator(self)
        self.buttons_by_char = {}

        # Setup layout architecture
        self._build_styles()
        self._create_layout_skeleton()
        self._build_top_bar()
        self._build_displays()
        self._build_grids()
        self._build_history_sidebar()
        self._bind_keys()

    def _build_styles(self):
        # Premium dark color palette
        self.clr_bg = "#0F0F12"
        self.clr_display = "#16161C"
        self.clr_btn_num = "#202026"
        self.clr_btn_num_hover = "#2A2A32"
        self.clr_btn_num_click = "#1A1A20"
        
        self.clr_btn_op = "#7C4DFF"
        self.clr_btn_op_hover = "#966BFF"
        self.clr_btn_op_click = "#622DFF"
        
        self.clr_btn_spec = "#30303A"
        self.clr_btn_spec_hover = "#40404C"
        self.clr_btn_spec_click = "#202028"
        self.clr_text_cyan = "#00E5FF"
        
        self.clr_btn_sci = "#1A2035"
        self.clr_btn_sci_hover = "#252D4A"
        self.clr_btn_sci_click = "#141828"
        self.clr_text_sci = "#A0C0FF"

        self.font_btn = ("Segoe UI Semibold", 13)
        self.font_btn_small = ("Segoe UI Semibold", 11)

    def _create_layout_skeleton(self):
        # Multi-paned layout structure
        # Left sidebar (Scientific), Center (Standard Grid), Right sidebar (History)
        self.header_frame = tk.Frame(self.root, bg=self.clr_bg, height=45)
        self.header_frame.pack(fill="x", padx=15, pady=(10, 0))
        self.header_frame.pack_propagate(False)

        self.display_frame = tk.Frame(self.root, bg=self.clr_display, bd=0)
        self.display_frame.pack(fill="x", padx=15, pady=10)

        # Wrap dynamic panels in a single horizontal packing container
        self.panel_container = tk.Frame(self.root, bg=self.clr_bg)
        self.panel_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # We'll put standard_frame, scientific_frame and history_frame inside this container.
        self.scientific_frame = tk.Frame(self.panel_container, bg=self.clr_bg)
        self.standard_frame = tk.Frame(self.panel_container, bg=self.clr_bg)
        self.history_frame = tk.Frame(self.panel_container, bg="#121216", width=220)

        # Standard grid is always displayed first
        self.standard_frame.pack(side="left", fill="both", expand=True)

    def _build_top_bar(self):
        # Elegant top utility control bar
        # Scientific Toggle
        self.sci_toggle_btn = tk.Label(
            self.header_frame, text="SCIENTIFIC", fg="#80808C", bg=self.clr_bg,
            font=("Segoe UI Bold", 9), cursor="hand2", padx=8, pady=4
        )
        self.sci_toggle_btn.pack(side="left")
        self.sci_toggle_btn.bind("<Button-1>", lambda e: self.toggle_scientific())

        # History Toggle
        self.hist_toggle_btn = tk.Label(
            self.header_frame, text="HISTORY", fg="#80808C", bg=self.clr_bg,
            font=("Segoe UI Bold", 9), cursor="hand2", padx=8, pady=4
        )
        self.hist_toggle_btn.pack(side="right")
        self.hist_toggle_btn.bind("<Button-1>", lambda e: self.toggle_history())

        # Active Mode Indicators
        self.mode_label = tk.Label(
            self.header_frame, text="DEG", fg=self.clr_text_cyan, bg=self.clr_bg,
            font=("Segoe UI Semibold", 9)
        )
        self.mode_label.pack(side="left", padx=20)
        self.mode_label.pack_forget()  # Hidden by default, shown in scientific mode

    def _build_displays(self):
        # Equation string display (top line)
        self.eq_lbl = tk.Label(
            self.display_frame, text="", bg=self.clr_display, fg="#80808C",
            font=("Segoe UI", 12), anchor="e"
        )
        self.eq_lbl.pack(fill="x", padx=15, pady=(12, 4))

        # Current input / calculation result display (bottom line)
        self.res_lbl = tk.Label(
            self.display_frame, text="0", bg=self.clr_display, fg="#FFFFFF",
            font=("Segoe UI Semibold", 28), anchor="e"
        )
        self.res_lbl.pack(fill="x", padx=15, pady=(0, 12))

    def _build_grids(self):
        # Configure weight ratios to make grids dynamically responsive
        for frame in (self.standard_frame, self.scientific_frame):
            for i in range(5):
                frame.rowconfigure(i, weight=1, uniform="equal")
            for j in range(4):
                frame.columnconfigure(j, weight=1, uniform="equal")

        # Standard layout configuration
        std_buttons = [
            ("C", self.clear_all, self.clr_btn_spec, self.clr_btn_spec_hover, self.clr_btn_spec_click, self.clr_text_cyan),
            ("⌫", self.backspace, self.clr_btn_spec, self.clr_btn_spec_hover, self.clr_btn_spec_click, self.clr_text_cyan),
            ("%", lambda: self.append_op("%"), self.clr_btn_spec, self.clr_btn_spec_hover, self.clr_btn_spec_click, self.clr_text_cyan),
            ("÷", lambda: self.append_op("÷"), self.clr_btn_op, self.clr_btn_op_hover, self.clr_btn_op_click, "#FFFFFF"),
            
            ("7", lambda: self.append_num("7"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("8", lambda: self.append_num("8"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("9", lambda: self.append_num("9"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("×", lambda: self.append_op("×"), self.clr_btn_op, self.clr_btn_op_hover, self.clr_btn_op_click, "#FFFFFF"),
            
            ("4", lambda: self.append_num("4"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("5", lambda: self.append_num("5"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("6", lambda: self.append_num("6"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("-", lambda: self.append_op("-"), self.clr_btn_op, self.clr_btn_op_hover, self.clr_btn_op_click, "#FFFFFF"),
            
            ("1", lambda: self.append_num("1"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("2", lambda: self.append_num("2"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("3", lambda: self.append_num("3"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("+", lambda: self.append_op("+"), self.clr_btn_op, self.clr_btn_op_hover, self.clr_btn_op_click, "#FFFFFF"),
            
            ("+/-", self.toggle_sign, self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("0", lambda: self.append_num("0"), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            (".", lambda: self.append_num("."), self.clr_btn_num, self.clr_btn_num_hover, self.clr_btn_num_click, "#FFFFFF"),
            ("=", self.calculate, self.clr_btn_op, self.clr_btn_op_hover, self.clr_btn_op_click, "#FFFFFF"),
        ]

        idx = 0
        for r in range(5):
            for c in range(4):
                label, cmd, bg, hvr, clk, fg = std_buttons[idx]
                btn = ModernButton(
                    self.standard_frame, text=label, command=cmd,
                    bg_color=bg, hover_color=hvr, pressed_color=clk,
                    text_color=fg, font=self.font_btn
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                self.buttons_by_char[label] = btn
                idx += 1

        # Scientific layout configuration (3 columns grid)
        self.scientific_frame.columnconfigure(0, weight=1, uniform="equal")
        self.scientific_frame.columnconfigure(1, weight=1, uniform="equal")
        self.scientific_frame.columnconfigure(2, weight=1, uniform="equal")

        sci_buttons = [
            ("(", lambda: self.append_num("("), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            (")", lambda: self.append_num(")"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("^", lambda: self.append_op("^"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            
            ("sin", lambda: self.append_func("sin"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("cos", lambda: self.append_func("cos"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("tan", lambda: self.append_func("tan"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            
            ("log", lambda: self.append_func("log"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("ln", lambda: self.append_func("ln"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("√", lambda: self.append_func("sqrt"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            
            ("π", lambda: self.append_num("pi"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("e", lambda: self.append_num("e"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("x!", lambda: self.append_op("!"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            
            ("x²", self.append_square, self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("abs", lambda: self.append_func("abs"), self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_sci),
            ("RAD", self.toggle_deg_rad, self.clr_btn_sci, self.clr_btn_sci_hover, self.clr_btn_sci_click, self.clr_text_cyan),
        ]

        idx = 0
        for r in range(5):
            for c in range(3):
                label, cmd, bg, hvr, clk, fg = sci_buttons[idx]
                btn = ModernButton(
                    self.scientific_frame, text=label, command=cmd,
                    bg_color=bg, hover_color=hvr, pressed_color=clk,
                    text_color=fg, font=self.font_btn_small
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                self.buttons_by_char[label] = btn
                idx += 1

    def _build_history_sidebar(self):
        # History panel wrapper
        header = tk.Frame(self.history_frame, bg="#121216", height=40)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)

        lbl = tk.Label(header, text="HISTORY", bg="#121216", fg="#FFFFFF", font=("Segoe UI Bold", 10))
        lbl.pack(side="left")

        clear_btn = tk.Label(
            header, text="CLEAR", bg="#121216", fg="#FF5252",
            font=("Segoe UI Bold", 8), cursor="hand2"
        )
        clear_btn.pack(side="right")
        clear_btn.bind("<Button-1>", lambda e: self.clear_history())

        # Scrollable items frame
        self.history_list = ScrollableHistoryFrame(self.history_frame, self.restore_history, bg_color="#121216")
        self.history_list.pack(fill="both", expand=True)

    def _bind_keys(self):
        # Window key bindings for smooth keyboard calculations
        self.root.bind("<Key>", self._on_keypress)
        # Prevent keys like Enter, Space or Backspace triggering standard Tkinter default focus actions
        self.root.bind("<Return>", lambda e: self.trigger_key_action("="))
        self.root.bind("<BackSpace>", lambda e: self.trigger_key_action("⌫"))
        self.root.bind("<Escape>", lambda e: self.trigger_key_action("C"))
        
    def _on_keypress(self, event):
        char = event.char
        keysym = event.keysym
        
        # Translate special key names
        if char == "*":
            self.trigger_key_action("×")
        elif char == "/":
            self.trigger_key_action("÷")
        elif char in ("+", "-", "%", ".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "(", ")"):
            self.trigger_key_action(char)
        elif char == "=":
            self.trigger_key_action("=")

    def trigger_key_action(self, char):
        # Triggers button flash effect and runs corresponding command
        if char in self.buttons_by_char:
            self.buttons_by_char[char].flash()

    # Core Action Callbacks
    def append_num(self, val):
        if self.result_shown:
            self.expression = ""
            self.result_shown = False
        
        # Add multiplying operator implicitly if inserting constants directly after closing parens or numbers
        if val in ("pi", "e") and self.expression and (self.expression[-1].isdigit() or self.expression[-1] in (")", "i", "e")):
            self.expression += " × "

        # Append value
        if val == "pi":
            self.expression += "pi"
        elif val == "e":
            self.expression += "e"
        else:
            self.expression += val
            
        self.update_display()

    def append_op(self, op):
        self.result_shown = False
        if op == "!":
            # Factorial is suffix
            self.expression += "!"
        else:
            # Wrap standard operators with readable spaces
            self.expression += f" {op} "
        self.update_display()

    def append_func(self, func_name):
        if self.result_shown:
            self.expression = ""
            self.result_shown = False
            
        # Add implicit multiplying operator if needed
        if self.expression and (self.expression[-1].isdigit() or self.expression[-1] in (")", "i", "e")):
            self.expression += " × "
            
        self.expression += f"{func_name}("
        self.update_display()

    def append_square(self):
        self.result_shown = False
        self.expression += "^2"
        self.update_display()

    def toggle_sign(self):
        self.result_shown = False
        if not self.expression:
            self.expression = "-"
        elif self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression
        self.update_display()

    def backspace(self):
        self.result_shown = False
        if not self.expression:
            return
            
        # Clear double/triple-letter functions or spaces at the end
        if self.expression.endswith(" "):
            self.expression = self.expression[:-3]  # remove space operator space
        elif self.expression.endswith("sin(") or self.expression.endswith("cos(") or self.expression.endswith("tan(") or self.expression.endswith("log(") or self.expression.endswith("abs("):
            self.expression = self.expression[:-4]
        elif self.expression.endswith("ln("):
            self.expression = self.expression[:-3]
        elif self.expression.endswith("sqrt("):
            self.expression = self.expression[:-5]
        elif self.expression.endswith("pi"):
            self.expression = self.expression[:-2]
        else:
            self.expression = self.expression[:-1]
            
        self.update_display()

    def clear_all(self):
        self.expression = ""
        self.result_shown = False
        self.res_lbl.config(fg="#FFFFFF")  # Reset error color
        self.update_display()

    def calculate(self):
        if not self.expression:
            return

        cleaned_expr = self.expression
        
        # Replace suffixes or factorials before parsing
        # Simple factorial parser replacement for single numbers or constants, e.g. 5! -> fact(5)
        # Note: If it's a complex equation, we can recursively map 'x!' to 'fact(x)'.
        if "!" in cleaned_expr:
            # Simple conversion for postfix factorial e.g. 5! -> fact(5)
            # Find integer preceding '!'
            import re
            # Regex to find integers/constants followed by !
            cleaned_expr = re.sub(r'(\b\d+|\bpi|\be)!', r'fact(\1)', cleaned_expr)

        try:
            result = self.evaluator.evaluate(cleaned_expr)
            
            # Record in history
            self.history_items.append((self.expression, result))
            self.history_list.add_history_item(self.expression, result)

            self.eq_lbl.config(text=f"{self.expression} =")
            self.expression = str(result)
            self.res_lbl.config(fg="#FFFFFF")
            self.result_shown = True
        except ZeroDivisionError as e:
            self.eq_lbl.config(text=f"{self.expression}")
            self.expression = ""
            self.res_lbl.config(fg="#FF5252") # Alert red
            self.res_lbl.config(text=str(e))
            self.result_shown = True
            return
        except OverflowError as e:
            self.eq_lbl.config(text=f"{self.expression}")
            self.expression = ""
            self.res_lbl.config(fg="#FF5252")
            self.res_lbl.config(text=str(e))
            self.result_shown = True
            return
        except Exception as e:
            error_msg = str(e) if "Math Error" in str(e) else "Syntax Error"
            self.eq_lbl.config(text=f"{self.expression}")
            self.expression = ""
            self.res_lbl.config(fg="#FF5252")
            self.res_lbl.config(text=error_msg)
            self.result_shown = True
            return

        self.update_display()

    def update_display(self):
        # Truncate expressions for very long inputs to prevent screen break
        disp_expr = self.expression
        if len(disp_expr) > 28:
            disp_expr = "..." + disp_expr[-25:]
            
        if self.result_shown:
            self.res_lbl.config(text=disp_expr)
        else:
            self.res_lbl.config(text=disp_expr if disp_expr else "0")

    # Panel Layout Modifiers
    def toggle_scientific(self):
        self.scientific_active = not self.scientific_active
        if self.scientific_active:
            # Change toggle style
            self.sci_toggle_btn.config(fg=self.clr_text_cyan)
            # Make sure history frame is shifted to allow space
            self.root.geometry("560x650")
            self.scientific_frame.pack(side="left", fill="both", expand=True, before=self.standard_frame)
            self.mode_label.pack(side="left", padx=20)
        else:
            self.sci_toggle_btn.config(fg="#80808C")
            self.scientific_frame.pack_forget()
            self.mode_label.pack_forget()
            if not self.history_active:
                self.root.geometry("400x650")
            else:
                self.root.geometry("620x650")

    def toggle_history(self):
        self.history_active = not self.history_active
        if self.history_active:
            self.hist_toggle_btn.config(fg=self.clr_text_cyan)
            # Expand window size to house sidebar nicely
            w = 780 if self.scientific_active else 620
            self.root.geometry(f"{w}x650")
            self.history_frame.pack(side="right", fill="both", before=self.standard_frame if self.scientific_active else None)
        else:
            self.hist_toggle_btn.config(fg="#80808C")
            self.history_frame.pack_forget()
            w = 560 if self.scientific_active else 400
            self.root.geometry(f"{w}x650")

    def toggle_deg_rad(self):
        self.is_degrees = not self.is_degrees
        mode_btn = self.buttons_by_char["RAD"]
        if self.is_degrees:
            self.mode_label.config(text="DEG")
            mode_btn.text = "RAD"
        else:
            self.mode_label.config(text="RAD")
            mode_btn.text = "DEG"
        # Force button redraw to update label
        mode_btn._draw()

    def restore_history(self, equation, result):
        self.expression = equation
        self.result_shown = False
        self.res_lbl.config(fg="#FFFFFF")
        self.update_display()

    def clear_history(self):
        self.history_items.clear()
        self.history_list.clear()


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorUI(root)
    root.mainloop()
