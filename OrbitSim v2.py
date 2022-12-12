import tkinter as tk
from tkinter.colorchooser import askcolor
from dataclasses import dataclass, field
from itertools import count
import math
from random import randint
from copy import copy


class OrbitSimGui:

    def __init__(self) -> None:

        self.vect_scale = 0
        self.grid_scale = 100

        self.master = self._setup_master()
        self.widgets = self._setup_widgets()

        self.osc = OrbitSimComp()

        self._setup_input()

        self.pix = tk.PhotoImage(width=1, height=1)

        self.master.mainloop()

    @staticmethod
    def _setup_master() -> tk.Tk:

        master = tk.Tk()
        master.geometry("800x550")
        master.resizable(False, False)
        master.title("OrbitSim")

        return master

    def _setup_widgets(self) -> dict:

        widgets = dict()

        master_frame = tk.Frame(self.master)
        master_frame.pack(expand=True, fill=tk.BOTH)

        top_frame = tk.Frame(master_frame, width=800, height=50)
        top_frame.pack(side=tk.TOP)
        top_frame.pack_propagate(False)

        settings_frame = tk.Frame(top_frame, borderwidth=2, relief=tk.RAISED, width=800, height=50)
        settings_frame.pack()
        settings_frame.pack_propagate(False)

        tk.Label(settings_frame, text="Grid Scale: ").pack(side=tk.LEFT, padx=1)

        widgets.update({"grid_scale_textvar": tk.StringVar(value=str(self.grid_scale))})

        tk.Entry(settings_frame, textvariable=widgets["grid_scale_textvar"], width=4).pack(side=tk.LEFT, padx=1)

        tk.Label(settings_frame, text="10^").pack(side=tk.LEFT, padx=1)

        widgets.update({"space_scale_textvar": tk.StringVar(value='0')})

        tk.Entry(settings_frame, textvariable=widgets["space_scale_textvar"], width=3).pack(side=tk.LEFT, padx=1)

        tk.Label(settings_frame, text='m').pack(side=tk.LEFT, padx=1)

        tk.Label(settings_frame, text="Vector Display Scale: 10^").pack(side=tk.LEFT, padx=1)

        widgets.update({"vect_scale_textvar": tk.StringVar(value='0')})

        tk.Entry(settings_frame, textvariable=widgets["vect_scale_textvar"], width=3).pack(side=tk.LEFT, padx=1)

        tk.Label(settings_frame, text="Path Iterations:").pack(side=tk.LEFT, padx=1)

        widgets.update({"path_len_textvar": tk.StringVar(value='100')})

        tk.Entry(settings_frame, textvariable=widgets["path_len_textvar"], width=4).pack(side=tk.LEFT, padx=1)

        tk.Label(settings_frame, text="Path Resolution:").pack(side=tk.LEFT, padx=1)

        widgets.update({"path_res_textvar": tk.StringVar(value='1')})

        tk.Entry(settings_frame, textvariable=widgets["path_res_textvar"], width=4).pack(side=tk.LEFT, padx=1)

        widgets.update({"show_path_vect_checkvar": tk.IntVar(value=0)})

        tk.Checkbutton(settings_frame, onvalue=1, offvalue=0, text="Show Path Vectors", variable=widgets["show_path_vect_checkvar"]).pack(side=tk.LEFT, padx=1)

        bottom_frame = tk.Frame(master_frame, width=800, height=500)
        bottom_frame.pack(side=tk.BOTTOM)
        bottom_frame.pack_propagate(False)

        canvas_frame = tk.Frame(bottom_frame, width=500, height=500)
        canvas_frame.pack(side=tk.LEFT)
        canvas_frame.pack_propagate(False)

        widgets.update({"canvas": tk.Canvas(canvas_frame, bg="BLACK", width=500, height=500)})
        widgets["canvas"].pack()

        for i in range(500//self.grid_scale):
            widgets["canvas"].create_line(i * self.grid_scale, 0, i * self.grid_scale, 500, fill='#333333', tags="grid")
            widgets["canvas"].create_line(0, i * self.grid_scale, 500, i * self.grid_scale, fill='#333333', tags="grid")

        menu_frame = tk.Frame(bottom_frame, width=300, height=500)
        menu_frame.pack(side=tk.RIGHT)
        menu_frame.pack_propagate(False)

        objs_frame = tk.Frame(menu_frame, borderwidth=2, relief=tk.SUNKEN, width=300, height=450)
        objs_frame.pack()
        objs_frame.pack_propagate(False)

        widgets.update({"objs_scrollable_canvas": tk.Canvas(objs_frame, width=280, height=450, highlightthickness=0)})
        widgets["objs_scrollable_canvas"].pack(side=tk.LEFT)

        objs_scrollbar = tk.Scrollbar(objs_frame, command=widgets["objs_scrollable_canvas"].yview)
        objs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        widgets.update({"objs_scrollable_frame": tk.Frame(widgets["objs_scrollable_canvas"], highlightthickness=0)})
        widgets["objs_scrollable_canvas"].create_window((0, 0), window=widgets["objs_scrollable_frame"],
                                                        anchor=tk.NW, width=280)

        widgets["objs_scrollable_frame"].bind(
            "<Configure>",
            lambda e: widgets["objs_scrollable_canvas"].configure(
                scrollregion=widgets["objs_scrollable_canvas"].bbox(tk.ALL)
            )
        )

        widgets["objs_scrollable_canvas"].configure(yscrollcommand=objs_scrollbar.set)

        new_obj_frame = tk.Frame(menu_frame, borderwidth=2, relief=tk.RAISED, width=300, height=50)
        new_obj_frame.pack(side=tk.BOTTOM)
        new_obj_frame.pack_propagate(False)

        widgets.update({"new_bttn": tk.Button(new_obj_frame, text="New")})
        widgets["new_bttn"].pack(side=tk.LEFT, padx=4)

        widgets.update({"rad_textvar": tk.StringVar(value='30')})

        tk.Entry(new_obj_frame, textvariable=widgets["rad_textvar"], width=4).pack(side=tk.RIGHT, padx=4)

        tk.Label(new_obj_frame, text="Radius:").pack(side=tk.RIGHT, padx=1)

        widgets.update({"mass_mult_textvar": tk.StringVar(value='0')})

        tk.Entry(new_obj_frame, textvariable=widgets["mass_mult_textvar"], width=3).pack(side=tk.RIGHT, padx=1)

        tk.Label(new_obj_frame, text="* 10^").pack(side=tk.RIGHT, padx=1)

        widgets.update({"mass_textvar": tk.StringVar(value='0')})

        tk.Entry(new_obj_frame, textvariable=widgets["mass_textvar"], width=5).pack(side=tk.RIGHT, padx=1)

        tk.Label(new_obj_frame, text="Mass:").pack(side=tk.RIGHT, padx=1)

        return widgets

    def _setup_input(self) -> None:

        self.widgets["canvas"].bind('<Button-1>', self._select_obj)

        self.widgets["canvas"].bind('<B1-Motion>', self._move_obj)

        self.master.bind('<Key>', self._keyboard_handler)

        self.widgets["new_bttn"].configure(command=self._new_bttn_callback)

        self.widgets["vect_scale_textvar"].trace('w', self._update_vect_scale)

        self.widgets["space_scale_textvar"].trace('w', self._update_space_scale)

        self.widgets["grid_scale_textvar"].trace('w', self._update_grid_scale)

        self.widgets["path_len_textvar"].trace('w', self._update_path_len)

        self.widgets["path_res_textvar"].trace('w', self._update_path_res)

        self.widgets["show_path_vect_checkvar"].trace('w', self._toggle_path_vect)

    def _update_vect_scale(self, *args):

        scale = self.widgets["vect_scale_textvar"].get()

        scale = (int(scale) if len([c for c in scale if c.isalpha()]) == 0 else 0) if scale != '' and scale != '-' else 0

        self.vect_scale = scale

        self._update_vectors()

    def _update_space_scale(self, *args):

        scale = self.widgets["space_scale_textvar"].get()

        scale = int(scale) if scale != '' and scale.isdigit() else 0

        self.osc.space_scale = scale

        self.osc.compute_gforces(self.osc.objects)
        self._update_vectors()
        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _update_grid_scale(self, *args):

        scale = self.widgets["grid_scale_textvar"].get()

        scale = int(scale) if scale != '' and scale != '0' and scale.isdigit() else 100

        self.grid_scale = scale

        lines = self.widgets["canvas"].find_withtag("grid")

        for l in lines:
            self.widgets["canvas"].delete(l)

        if self.grid_scale != 0:
            for i in range(500//self.grid_scale):
                a = self.widgets["canvas"].create_line(i * self.grid_scale, 0, i * self.grid_scale, 500, fill='#333333', tags="grid")
                b = self.widgets["canvas"].create_line(0, i * self.grid_scale, 500, i * self.grid_scale, fill='#333333', tags="grid")
                self.widgets["canvas"].tag_lower(a)
                self.widgets["canvas"].tag_lower(b)

    def _update_path_len(self, *args):

        var = self.widgets["path_len_textvar"].get()

        var = int(var) if var != '' and var.isdigit() else 0

        self.osc.path_iterations = var

        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _update_path_res(self, *args):

        var = self.widgets["path_res_textvar"].get()

        var = float(var) if var != '0' and var != '0.' and var.replace('.', '', 1).isdigit() else 1

        self.osc.path_resolution = var

        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _toggle_path_vect(self, *args):

        var = self.widgets["show_path_vect_checkvar"].get()

        self.osc.path_vectors = True if var else False

        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _select_obj(self, event):

        self.master.focus()

        for obj in self.osc.objects:

            if obj.x - obj.radius < event.x < obj.x + obj.radius \
                    and obj.y - obj.radius < event.y < obj.y + obj.radius:

                obj_id = self.widgets["canvas"].find_withtag("Obj-" + str(obj.identifier))[0]

                if not obj.selected:

                    obj.selected = True

                    c = self.widgets["canvas"].coords(obj_id)

                    self.widgets["canvas"].create_oval(c[0] - 5, c[1] - 5, c[2] + 5, c[3] + 5, outline="#FFFFFF", tags="Obj-" + str(obj.identifier) + "_selected")

            else:

                if obj.selected:

                    obj.selected = False

                    self.widgets["canvas"].delete(self.widgets["canvas"].find_withtag("Obj-" + str(obj.identifier) + "_selected")[0])

    def _move_obj(self, event):

        for obj in self.osc.objects:

            if obj.selected:

                obj_id = self.widgets["canvas"].find_withtag("Obj-" + str(obj.identifier))[0]
                select_id = self.widgets["canvas"].find_withtag("Obj-" + str(obj.identifier) + "_selected")[0]

                if obj.x - obj.radius < event.x < obj.x + obj.radius \
                   and obj.y - obj.radius < event.y < obj.y + obj.radius:

                    x = event.x - obj.x
                    y = event.y - obj.y

                    for o in self.osc.objects:

                        if o.identifier != obj.identifier:

                            d = math.sqrt((math.pow((obj.x + x - o.x), 2) + math.pow((obj.y + y - o.y), 2)))
                            r = obj.radius + o.radius

                            if d <= r:

                                return

                    obj.x += x
                    obj.y += y

                    self.widgets["canvas"].move(obj_id, x, y)
                    self.widgets["canvas"].move(select_id, x, y)

        self.osc.compute_gforces(self.osc.objects)
        self._update_vectors()
        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _keyboard_handler(self, event):

        if event.char == 'e':
            self.osc.path_iterations += 10
            self.widgets["path_len_textvar"].set(str(self.osc.path_iterations))

        if event.char == 'q':
            self.osc.path_iterations -= 10
            self.widgets["path_len_textvar"].set(str(self.osc.path_iterations))

        if event.char == 'z':
            if self.osc.path_resolution >= 1:
                self.osc.path_resolution += 1
            else:
                self.osc.path_resolution += 0.1

            self.osc.path_resolution = round(self.osc.path_resolution, 2)
            self.widgets["path_res_textvar"].set(str(self.osc.path_resolution))

        if event.char == 'c':
            if self.osc.path_resolution > 0.1:
                if self.osc.path_resolution > 1:
                    self.osc.path_resolution -= 1
                else:
                    self.osc.path_resolution -= 0.1

                self.osc.path_resolution = round(self.osc.path_resolution, 2)
                self.widgets["path_res_textvar"].set(str(self.osc.path_resolution))

        for obj in self.osc.objects:

            if obj.selected:

                obj_widg_name = "Obj-" + str(obj.identifier)

                if event.char == 'w':
                    obj.a_y -= 1

                    v_m = (obj.a_x ** 2 + obj.a_y ** 2) ** 0.5
                    v_d = math.degrees(math.atan2(obj.a_y * -1, obj.a_x))

                    self.widgets[obj_widg_name + "_v_m_textvar"].set(round(v_m))
                    self.widgets[obj_widg_name + "_v_d_textvar"].set(round(v_d))

                if event.char == 'a':
                    obj.a_x -= 1

                    v_m = (obj.a_x ** 2 + obj.a_y ** 2) ** 0.5
                    v_d = math.degrees(math.atan2(obj.a_y * -1, obj.a_x))

                    self.widgets[obj_widg_name + "_v_m_textvar"].set(round(v_m))
                    self.widgets[obj_widg_name + "_v_d_textvar"].set(round(v_d))

                if event.char == 's':
                    obj.a_y += 1

                    v_m = (obj.a_x ** 2 + obj.a_y ** 2) ** 0.5
                    v_d = math.degrees(math.atan2(obj.a_y * -1, obj.a_x))

                    self.widgets[obj_widg_name + "_v_m_textvar"].set(round(v_m))
                    self.widgets[obj_widg_name + "_v_d_textvar"].set(round(v_d))

                if event.char == 'd':
                    obj.a_x += 1

                    v_m = (obj.a_x ** 2 + obj.a_y ** 2) ** 0.5
                    v_d = math.degrees(math.atan2(obj.a_y * -1, obj.a_x))

                    self.widgets[obj_widg_name + "_v_m_textvar"].set(round(v_m))
                    self.widgets[obj_widg_name + "_v_d_textvar"].set(round(v_d))

        self._update_vectors()
        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _new_bttn_callback(self):

        def __get_new_obj_prop():

            mass = self.widgets["mass_textvar"].get()
            mass_mult = self.widgets["mass_mult_textvar"].get()
            rad = self.widgets["rad_textvar"].get()

            mass = int(mass) if mass != '' and mass.isdigit() else 0
            mass_mult = int(mass_mult) if mass_mult != '' and mass_mult.isdigit() else 0
            rad = int(rad) if rad != '' and rad.isdigit() else 0

            return mass, mass_mult, rad

        prop = __get_new_obj_prop()

        self._add_obj_field(self.osc.add_obj(prop[0], prop[1], prop[2]))

    def _add_obj_field(self, obj) -> None:

        obj_widg_name = "Obj-" + str(obj.identifier)

        self.widgets.update({obj_widg_name + "_frame": tk.Frame(self.widgets["objs_scrollable_frame"], width=280, height=100, relief=tk.RIDGE, borderwidth=2)})
        self.widgets[obj_widg_name + "_frame"].pack(fill=tk.X)
        self.widgets[obj_widg_name + "_frame"].pack_propagate(False)

        top_frame = tk.Frame(self.widgets[obj_widg_name + "_frame"], width=280, height=70)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Name:").grid(row=0, column=0, pady=2)

        tk.Label(top_frame, text=obj_widg_name).grid(row=0, column=1, pady=2)

        self.widgets.update({obj_widg_name + "_color_button": tk.Button(top_frame, compound="center", bg=obj.color, width=30, height=10, image=self.pix, command=lambda: self._update_obj_color(obj))})
        self.widgets[obj_widg_name + "_color_button"].grid(row=0, column=4, padx=7)

        self.widgets.update({obj_widg_name + "_del_button": tk.Button(top_frame, text="X", width=10, height=10, compound="center", image=self.pix, command= lambda: self._dell_obj(obj))})
        self.widgets[obj_widg_name + "_del_button"].grid(row=0, column=6)

        tk.Label(top_frame, text="Mass:").grid(row=2, column=0, pady=2)

        mass = self.widgets["mass_textvar"].get()
        self.widgets.update({obj_widg_name + "_mass_textvar": tk.StringVar(value=mass if mass != '' and mass.isdigit() else 0)})

        tk.Entry(top_frame, textvariable=self.widgets[obj_widg_name + "_mass_textvar"], width=5).grid(row=2, column=1, pady=2)

        tk.Label(top_frame, text="* 10^").grid(row=2, column=2, pady=2)

        mass_mult = self.widgets["mass_mult_textvar"].get()
        self.widgets.update({obj_widg_name + "_mult_textvar": tk.StringVar(value=mass_mult if mass_mult != '' and mass_mult.isdigit() else 0)})

        tk.Entry(top_frame, width=3, textvariable=self.widgets[obj_widg_name + "_mult_textvar"]).grid(row=2, column=3, pady=2)

        tk.Label(top_frame, text="Radius:").grid(row=3, column=0, pady=2)

        rad = self.widgets["rad_textvar"].get()
        self.widgets.update({obj_widg_name + "_rad_textvar": tk.StringVar(value=rad if rad != '' and rad.isdigit() else str(0))})

        tk.Entry(top_frame, textvariable=self.widgets[obj_widg_name + "_rad_textvar"], width=5).grid(row=3, column=1, pady=2)

        self.widgets.update({obj_widg_name + "_static_checkvar": tk.IntVar(value=obj.static)})

        tk.Checkbutton(top_frame, text="Static", variable=self.widgets[obj_widg_name + "_static_checkvar"], onvalue=1, offvalue=0).grid(row=3, column=2, pady=2)

        tk.Label(top_frame, text="V_m:").grid(row=2, column=5, pady=2)

        self.widgets.update({obj_widg_name + "_v_m_textvar": tk.StringVar(value="0")})

        tk.Entry(top_frame, textvariable=self.widgets[obj_widg_name + "_v_m_textvar"], width=5).grid(row=2, column=6, pady=2)

        tk.Label(top_frame, text="V_d").grid(row=3, column=5, pady=2)

        self.widgets.update({obj_widg_name + "_v_d_textvar": tk.StringVar(value="0")})

        tk.Entry(top_frame, textvariable=self.widgets[obj_widg_name + "_v_d_textvar"], width=5).grid(row=3, column=6, pady=2)

        bottom_frame = tk.Frame(self.widgets[obj_widg_name + "_frame"], width=280, height=30)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(bottom_frame, text="G_a:").pack(side=tk.LEFT, pady=2)

        self.widgets.update({obj_widg_name + "_g_a_textvar": tk.StringVar()})

        tk.Label(bottom_frame, textvariable=self.widgets[obj_widg_name + "_g_a_textvar"]).pack(side=tk.RIGHT, pady=2)

        top_frame.bind(
            "<MouseWheel>",
            lambda e: self.widgets["objs_scrollable_canvas"].yview_scroll(int(-1 * (e.delta / 120)), "units"))

        for widg in top_frame.winfo_children():
            widg.bind(
                "<MouseWheel>",
                lambda e: self.widgets["objs_scrollable_canvas"].yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.widgets[obj_widg_name + "_mass_textvar"].trace('w', lambda _, __, ___: self._mass_textvar_callback(obj))
        self.widgets[obj_widg_name + "_mult_textvar"].trace('w', lambda _, __, ___: self._mass_textvar_callback(obj))
        self.widgets[obj_widg_name + "_rad_textvar"].trace('w', lambda _, __, ___: self._rad_textvar_callback(obj))
        self.widgets[obj_widg_name + "_static_checkvar"].trace('w', lambda _, __, ___: self._static_checkvar_callback(obj))
        self.widgets[obj_widg_name + "_v_m_textvar"].trace('w', lambda _, __, ___: self._v_p_textvar_callback(obj))
        self.widgets[obj_widg_name + "_v_d_textvar"].trace('w', lambda _, __, ___: self._v_p_textvar_callback(obj))

        self.osc.compute_gforces(self.osc.objects)
        self.widgets[obj_widg_name + "_g_a_textvar"].set(str(obj.t_ga) + " m/s")

        self.widgets["canvas"].create_oval(obj.x - obj.radius, obj.y - obj.radius,
                                           obj.x + obj.radius, obj.y + obj.radius, fill=obj.color,
                                           tags=obj_widg_name)
        self.widgets["canvas"].create_line(obj.x, obj.y, obj.x + (obj.ga_x * math.pow(10, self.vect_scale)),
                                           obj.y + (obj.ga_y * math.pow(10, self.vect_scale)),
                                           arrow=tk.LAST, fill="#FF07FF", tags=obj_widg_name + "_gvect")
        self.widgets["canvas"].create_line(obj.x, obj.y, obj.x + obj.a_x, obj.y + obj.a_y,
                                           arrow=tk.LAST, fill="#009900", tags=obj_widg_name + "_vvect")

        self._update_vectors()
        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _mass_textvar_callback(self, obj):

        obj_widg_name = "Obj-" + str(obj.identifier)

        mass = self.widgets[obj_widg_name + "_mass_textvar"].get()
        mass_mult = self.widgets[obj_widg_name + "_mult_textvar"].get()

        mass = (int(mass) if int(mass) > 0 else 0) if mass != '' and mass.isdigit() else 0
        mass_mult = (int(mass_mult) if int(mass_mult) > 0 else 0) if mass_mult != '' and mass_mult.isdigit() else 0

        obj.mass = mass * pow(10, mass_mult)

        self.osc.compute_gforces(self.osc.objects)
        self._update_vectors()
        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _rad_textvar_callback(self, obj):

        obj_widg_name = "Obj-" + str(obj.identifier)

        rad = self.widgets[obj_widg_name + "_rad_textvar"].get()

        rad = (int(rad) if int(rad) > 0 else 0) if rad != '' and rad.isdigit() else 0

        obj.radius = rad

        self.widgets["canvas"].coords(self.widgets["canvas"].find_withtag(obj_widg_name)[0],
                                      obj.x - obj.radius, obj.y - obj.radius,
                                      obj.x + obj.radius, obj.y + obj.radius)
        if obj.selected:
            c = self.widgets["canvas"].coords(obj_widg_name)
            self.widgets["canvas"].coords(self.widgets["canvas"].find_withtag(obj_widg_name + "_selected")[0],
                                          c[0] - 5, c[1] - 5, c[2] + 5, c[3] + 5)

    def _static_checkvar_callback(self, obj):

        obj_widg_name = "Obj-" + str(obj.identifier)

        obj.static = True if self.widgets[obj_widg_name + "_static_checkvar"].get() else False

        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _v_p_textvar_callback(self, obj):

        obj_widg_name = "Obj-" + str(obj.identifier)

        m_var = self.widgets[obj_widg_name + "_v_m_textvar"].get()
        d_var = self.widgets[obj_widg_name + "_v_d_textvar"].get()

        if m_var.isdigit() and d_var.isdigit():

            m_var = m_var if m_var != '' else 0
            d_var = d_var if d_var != '' else 0

            obj.a_x = math.cos(math.radians(int(d_var) * -1)) * int(m_var)
            obj.a_y = math.sin(math.radians(int(d_var) * -1)) * int(m_var)

    def _update_obj_color(self, obj):

        obj_widg_name = "Obj-" + str(obj.identifier)

        color = askcolor(obj.color)[1]

        obj.color = color
        self.widgets[obj_widg_name + "_color_button"].configure(bg=color)
        self.widgets["canvas"].itemconfig(self.widgets["canvas"].find_withtag(obj_widg_name), fill=color)
        for p in self.widgets["canvas"].find_withtag("path"):
            self.widgets["canvas"].itemconfig(p, fill=color)

    def _dell_obj(self, obj):

        obj_widg_name = "Obj-" + str(obj.identifier)

        self.osc.objects.remove(obj)

        self.widgets[obj_widg_name + "_frame"].destroy()
        self.widgets["canvas"].delete(self.widgets["canvas"].find_withtag(obj_widg_name)[0])
        self.widgets["canvas"].delete(self.widgets["canvas"].find_withtag(obj_widg_name + "_gvect")[0])
        self.widgets["canvas"].delete(self.widgets["canvas"].find_withtag(obj_widg_name + "_vvect")[0])
        if obj.selected:
            self.widgets["canvas"].delete(self.widgets["canvas"].find_withtag(obj_widg_name + "_selected")[0])

        self.osc.compute_gforces(self.osc.objects)
        self._update_vectors()
        self.osc.compute_path(self.widgets["canvas"], self.vect_scale)

    def _update_vectors(self):

        for obj in self.osc.objects:

            obj_widg_name = "Obj-" + str(obj.identifier)

            self.widgets[obj_widg_name + "_g_a_textvar"].set(str(obj.t_ga) + " m/s")

            gvect_id = self.widgets["canvas"].find_withtag(obj_widg_name + "_gvect")[0]
            vvect_id = self.widgets["canvas"].find_withtag(obj_widg_name + "_vvect")[0]

            self.widgets["canvas"].coords(gvect_id,
                                          obj.x, obj.y,
                                          obj.x + (obj.ga_x * math.pow(10, self.vect_scale)),
                                          obj.y + (obj.ga_y * math.pow(10, self.vect_scale)))
            self.widgets["canvas"].coords(vvect_id,
                                          obj.x, obj.y,
                                          obj.x + (obj.a_x * math.pow(10, self.vect_scale * -1)),
                                          obj.y + (obj.a_y * math.pow(10, self.vect_scale * -1)))


class OrbitSimComp:

    G = 6.67 * 1e-11

    @dataclass
    class Object:
        identifier: int = field(default_factory=count().__next__)

        x: float = 0
        y: float = 0

        color: str = "#FFFFFF"
        selected: bool = False

        mass: float = 0
        radius: int = 30

        static: bool = True

        t_ga: float = 0
        t_gf: float = 0

        ga_x: float = 0
        ga_y: float = 0

        a_x: float = 0
        a_y: float = 0

    def __init__(self) -> None:

        self.space_scale = 0
        self.path_iterations = 100
        self.path_resolution = 1

        self.path_vectors = False

        self.objects = list()

    def add_obj(self, mass, mass_mult, rad) -> Object:

        def __find_pos():

            found_pos = False

            x = 0
            y = 0

            while not found_pos:

                x = randint(30, 470)
                y = randint(30, 470)

                check = 0

                if len(self.objects) > 0:

                    for o in self.objects:

                        d = math.sqrt((math.pow((x - o.x), 2) + math.pow((y - o.y), 2)))
                        r = rad + o.radius

                        if d >= r:

                            check += 1

                    if check == len(self.objects):

                        found_pos = True

                else:
                    found_pos = True

            return x, y

        pos = __find_pos()

        new_obj = self.Object(x=pos[0], y=pos[1], mass=mass * math.pow(10, mass_mult), radius=rad, color="#%06x" % randint(0, 0xFFFFFF))

        self.objects.append(new_obj)

        return self.objects[-1]

    def compute_gforces(self, objects):

        for obj1 in objects:

            forces = list()

            for obj2 in objects:

                if obj1.identifier != obj2.identifier:

                    dx = (obj2.x - obj1.x) * (10 ** self.space_scale)
                    dy = (obj2.y - obj1.y) * (10 ** self.space_scale)

                    distance = (dx ** 2 + dy ** 2) ** 0.5

                    # print(distance)

                    gf = ((obj1.mass * obj2.mass) / (distance ** 2)) * self.G

                    ga = gf / obj1.mass if obj1.mass != 0 else 0

                    ga_x = (dx / distance) * ga
                    ga_y = (dy / distance) * ga

                    forces.append((ga, ga_x, ga_y, gf))

            obj1.ga_x = 0
            obj1.ga_y = 0
            ta = 0
            tf = 0

            for f in forces:

                ta += f[0]
                obj1.ga_x += f[1]
                obj1.ga_y += f[2]
                tf += f[3]

            obj1.t_ga = ta
            obj1.t_gf = tf

    def compute_path(self, canvas, vect_scale):

        pathfinders = [copy(o) for o in self.objects]

        for p in canvas.find_withtag("path"):
            canvas.delete(p)
        for p in canvas.find_withtag("path_vect"):
            canvas.delete(p)

        for pf in pathfinders:

            if pf.static is False:

                # v_m = (pf.a_x ** 2 + pf.a_y ** 2) ** 0.5

                # o_r = pf.mass * v_m ** 2 / pf.t_gf

                t = 0

                v = 0

                prev_point = (pf.x, pf.y)

                while t < self.path_iterations:

                    pf.x = pf.x + pf.a_x * self.path_resolution + 0.5 * pf.ga_x * self.path_resolution ** 2
                    pf.y = pf.y + pf.a_y * self.path_resolution + 0.5 * pf.ga_y * self.path_resolution ** 2

                    pf.a_x = pf.a_x + pf.ga_x * self.path_resolution
                    pf.a_y = pf.a_y + pf.ga_y * self.path_resolution

                    brk = False

                    for o in self.objects:

                        if o.identifier != pf.identifier:

                            d = math.sqrt((math.pow((pf.x - o.x), 2) + math.pow((pf.y - o.y), 2)))

                            if d <= o.radius:
                                brk = True

                    if pf.x < -100 or pf.x > 600 or pf.y < -100 or pf.y > 600:
                        brk = True

                    """for i in range(10):
                        for j in range(10):

                            if (round(pf.x) + (i - 5), round(pf.y) + (j - 5)) in points:
                                brk = True"""

                    if brk is True:
                        break

                    self.compute_gforces(pathfinders)

                    # canvas.create_rectangle(pf.x-2, pf.y-2, pf.x+2, pf.y+2, fill=pf.color, outline="", tags="path")

                    if self.path_vectors is True:

                        if v % 10 == 1:

                            canvas.create_line(pf.x, pf.y,
                                               pf.x + (pf.ga_x * 10 ** vect_scale),
                                               pf.y + (pf.ga_y * 10 ** vect_scale),
                                               arrow=tk.LAST, fill="#FF07FF", tags="path_vect")
                            canvas.create_line(pf.x, pf.y, pf.x + pf.a_x, pf.y + pf.a_y,
                                               arrow=tk.LAST, fill="#009900", tags="path_vect")

                        v += 1

                    canvas.create_line(prev_point[0], prev_point[1], pf.x, pf.y,
                                       fill=pf.color,
                                       tags="path")

                    prev_point = (pf.x, pf.y)

                    t += self.path_resolution


def main() -> None:
    OrbitSimGui()


if __name__ == '__main__':
    main()
