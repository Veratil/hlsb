import functools
import struct
import pathlib
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import font
import bsf


INT32_MAX = ((1 << 31) - 1)
INT32_MIN = -(1 << 31)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.filepath = None
        self.currentSkin = None
        self.currentSycom = None
        self.ignoreUpdateSycom = True
        self.save_data = None
        fixedFont = font.nametofont('TkFixedFont')
        self.minsize(width=600, height=480)
        self.title("Hyper Light Save Breaker")
        self.option_add("*Font", fixedFont)
        self.__create_menubar()
        self.__create_notebook()
        self.__define_vars()
        self.__create_layout()

    def run(self):
        self.mainloop()

    def open_bsf(self):
        filetypes = (('BSF files', '*.bsf'),)
        filename = fd.askopenfilename(title='Open save file', initialdir='/', filetypes=filetypes)
        if not filename:
            return
        self.filepath = pathlib.Path(filename)
        backup = self.filepath.parent / (self.filepath.name + ".bak")
        shutil.copy(self.filepath, backup)
        self.raw = bsf.read_bsf(self.filepath)
        self.save_data = bsf.generate_save_struct(bsf.deflate_data(bytes(self.raw.data[0:])))
        self.__populate_skins()
        self.__activate_mats()
        self.__populate_equipment(self.save_data.active_character)
        self.__populate_world()
        self.__populate_vault()
        self.__populate_exe()

    def write_bsf(self):
        if not self.filepath:
            return
        new_save = bsf.generate_save_bytes(self.save_data)
        bsf.write_bsf(self.filepath, new_save)

    def __define_vars(self):
        # Gear
        self.equippedBlade = tk.StringVar(self)
        self.equippedRail = tk.StringVar(self)
        self.equippedAmp = tk.StringVar(self)
        self.equippedArmor = tk.StringVar(self)
        self.equippedHolo1 = tk.StringVar(self)
        self.equippedHolo2 = tk.StringVar(self)
        self.equippedHolo3 = tk.StringVar(self)
        self.equippedHolo4 = tk.StringVar(self)
        self.equippedHolo5 = tk.StringVar(self)
        self.equippedSycom = tk.StringVar(self)
        # Items
        self.itemBrightBlood = tk.IntVar(self, name="Items.BrightBlood")
        self.itemGoldRations = tk.IntVar(self, name="Items.GoldRations")
        self.itemAbyssStones = tk.IntVar(self, name="Items.AbyssStones")
        self.itemKeys = tk.IntVar(self, name="Items.Keys")
        self.itemCores = tk.IntVar(self, name="Items.Cores")
        self.itemPartialCores = tk.IntVar(self, name="Items.PartialCores")
        self.itemMaterials = tk.IntVar(self, name="Items.Materials")
        self.itemBrightBlood.trace_add("write", self.__updateIntVar)
        self.itemGoldRations.trace_add("write", self.__updateIntVar)
        self.itemAbyssStones.trace_add("write", self.__updateIntVar)
        self.itemKeys.trace_add("write", self.__updateIntVar)
        self.itemCores.trace_add("write", self.__updateIntVar)
        self.itemPartialCores.trace_add("write", self.__updateIntVar)
        self.itemMaterials.trace_add("write", self.__updateIntVar)
        # Sycom Attributes
        self.sycomHP = tk.IntVar(self, name="Attribute.Shield")
        self.sycomBattery = tk.IntVar(self, name="Attribute.Battery")
        self.sycomArmor = tk.IntVar(self, name="Attribute.Armor")
        self.sycomStrike = tk.IntVar(self, name="Attribute.Strike")
        self.sycomBlast = tk.IntVar(self, name="Attribute.Blast")
        self.sycomStam = tk.IntVar(self, name="Attribute.Stam")
        self.sycomCritChance = tk.IntVar(self, name="Attribute.CritChance")
        self.sycomCritDmg = tk.IntVar(self, name="Attribute.CritDmg")
        self.sycomOPS = tk.IntVar(self, name="Attribute.Luck")
        self.sycomHP.trace_add("write", self.__updateSycom)
        self.sycomBattery.trace_add("write", self.__updateSycom)
        self.sycomArmor.trace_add("write", self.__updateSycom)
        self.sycomStrike.trace_add("write", self.__updateSycom)
        self.sycomBlast.trace_add("write", self.__updateSycom)
        self.sycomStam.trace_add("write", self.__updateSycom)
        self.sycomCritChance.trace_add("write", self.__updateSycom)
        self.sycomCritDmg.trace_add("write", self.__updateSycom)
        self.sycomOPS.trace_add("write", self.__updateSycom)
        # World Data
        self.worldSeed1 = tk.IntVar(self, name="World.Seed1")
        self.worldSeed2 = tk.IntVar(self, name="World.Seed2")
        self.spawnPosX = tk.DoubleVar(self, name="Spawn.X")
        self.spawnPosY = tk.DoubleVar(self, name="Spawn.Y")
        self.spawnPosZ = tk.DoubleVar(self, name="Spawn.Z")
        self.rezsRemaining = tk.IntVar(self, name="World.Rezs")
        self.worldSeed1.trace_add("write", self.__updateIntVar)
        self.worldSeed2.trace_add("write", self.__updateIntVar)
        self.spawnPosX.trace_add("write", self.__updateDoubleVar)
        self.spawnPosY.trace_add("write", self.__updateDoubleVar)
        self.spawnPosZ.trace_add("write", self.__updateDoubleVar)
        self.rezsRemaining.trace_add("write", self.__updateIntVar)
        # EXEs
        self.exeTiers = tk.StringVar(self, name="EXE.Tiers")
        self.exeSlots = tk.StringVar(self, name="EXE.Slots")
        self.exeTiers.trace_add("write", self.__updateIntVar)
        self.exeSlots.trace_add("write", self.__updateIntVar)

    def print_data(self):
        if self.save_data:
            print(self.save_data)

    def __updateIntVar(self, varname, index, eventname):
        if self.save_data == None:
            return
        new_value = int(self.globalgetvar(varname))
        print(f"updating {varname} to {new_value}")
        match varname:
            case "Items.BrightBlood":
                self.save_data.bright_blood = new_value
            case "Items.GoldRations":
                self.save_data.gold_rations = new_value
            case "Items.AbyssStones":
                self.save_data.abyss_stones = new_value
            case "Items.Keys":
                self.save_data["keys"] = new_value
            case "Items.Cores":
                self.save_data.cores = new_value
            case "Items.PartialCores":
                self.save_data.partial_cores = new_value
            case "Items.Materials":
                self.save_data.materials = new_value
            case "EXE.Tiers":
                self.save_data.tiers_unlocked = new_value
            case "EXE.Slots":
                self.save_data.extra_slots = new_value
            case "World.Seed1":
                self.save_data.world_seed1 = new_value
            case "World.Seed2":
                self.save_data.world_seed2 = new_value
            case "World.Rezs":
                self.save_data.rezs_remaining = new_value

    def __updateDoubleVar(self, varname, index, eventname):
        if not self.save_data:
            return
        new_value = float(self.globalgetvar(varname))
        # restrict to 32bit float
        new_value = struct.unpack('f', struct.pack('f', new_value))[0]
        print(f"updating {varname} to {new_value}")
        match varname:
            case "Spawn.X":
                self.save_data.spawn_position.x = new_value
            case "Spawn.Y":
                self.save_data.spawn_position.y = new_value
            case "Spawn.Z":
                self.save_data.spawn_position.z = new_value

    def __updateSycom(self, varname, index, eventname):
        if not self.save_data:
            return
        if not self.currentSkin:
            return
        if self.ignoreUpdateSycom:
            return
        for sycom in self.save_data.sycom_upgrades.sycoms:
            if sycom.id != self.currentSycom:
                continue
            for attr in sycom.attributes:
                if attr.id[:-1] != varname:
                    continue
                print(f"updating {attr.id} to {attr.bonus}")
                attr.bonus = int(self.globalgetvar(varname))
                break
            else:
                print("adding new attribute to sycom bonuses")
                new_attr = bsf.AttributeBonus.build(dict(id=f"{varname}\x00", bonus=1))
                sycom.attributes.append(bsf.AttributeBonus.parse(new_attr))
            break
        else:
            pass
            #mb.showerror("Sycom Not Found", "sycom not found in save_data, this probably shouldn't happen")

    def __populate_skins(self):
        for child in self.skinsFrame.winfo_children():
            child.destroy()
        for skin in self.save_data.unlocked_characters.characters:
            tk.Button(self.skinsFrame, text=skin[14:], height=3,
                    command=functools.partial(self.__populate_equipment, skin)
                    ).pack(side=tk.LEFT)

    def __activate_mats(self):
        self.itemBrightBlood.set(str(self.save_data.bright_blood))
        self.itemGoldRations.set(str(self.save_data.gold_rations))
        self.itemAbyssStones.set(str(self.save_data.abyss_stones))
        self.itemKeys.set(str(self.save_data["keys"]))
        self.itemCores.set(str(self.save_data.cores))
        self.itemPartialCores.set(str(self.save_data.partial_cores))
        self.itemMaterials.set(str(self.save_data.materials))

    def __populate_equipment(self, skin_):
        self.equippedSycom.set("")
        self.equippedBlade.set("")
        self.equippedRail.set("")
        self.equippedArmor.set("")
        self.equippedHolo1.set("")
        self.equippedHolo2.set("")
        self.equippedHolo3.set("")
        self.equippedHolo4.set("")
        self.equippedHolo5.set("")
        for skin in self.save_data.equipped_items.characters:
            if skin.character != skin_:
                continue
            self.currentSkin = skin
            self.currentSycom = skin.equipped_sycom
            self.equippedSycom.set(skin.equipped_sycom[6:])
            for slotted_item in skin.equipment:
                self.__populate_item_slot(slotted_item)
            self.__populate_equipped_sycom_stats(skin.equipped_sycom)
            break
        else:
            mb.showerror("Cannot find skin", f"Could not find skin in the equipment struct: {skin_}")

    def __populate_item_slot(self, slotted_item):
        slot = slotted_item.slot
        match slotted_item.slot:
            case 0x01:  # blade
                self.equippedBlade.set(slotted_item.item.item_type[11:])
            case 0x02:  # rail
                self.equippedRail.set(slotted_item.item.item_type[10:])
            case 0x03:  # amp
                self.equippedAmp.set(slotted_item.item.item_type[13:])
            case 0x0E:  # armor
                self.equippedArmor.set(slotted_item.item.item_type[10:])
            case 0x09:  # holo1
                self.equippedHolo1.set(slotted_item.item.item_type[13:])
            case 0x0A:  # holo2
                self.equippedHolo2.set(slotted_item.item.item_type[13:])
            case 0x0B:  # holo3
                self.equippedHolo3.set(slotted_item.item.item_type[13:])
            case 0x0C:  # holo4
                self.equippedHolo4.set(slotted_item.item.item_type[13:])
            case 0x0D:  # holo5
                self.equippedHolo5.set(slotted_item.item.item_type[13:])
            case _:  # unknown
                mb.showerror("Unknown item slot", f"Parsed an unknown item slot: {slotted_item.slot}")

    def __createNewSycomUpgrade(self, sycom):
        self.save_data.sycom_upgrades.length += 1
        new_sycom = bsf.Sycom.build(dict(id=sycom, length=0, attributes=[]))
        parsed = bsf.Sycom.parse(new_sycom)
        self.save_data.sycom_upgrades.sycoms.append(parsed)

    def __populate_equipped_sycom_stats(self, sycom_):
        self.ignoreUpdateSycom = True
        self.sycomHP.set(0)
        self.sycomBattery.set(0)
        self.sycomArmor.set(0)
        self.sycomStrike.set(0)
        self.sycomBlast.set(0)
        self.sycomStam.set(0)
        self.sycomCritChance.set(0)
        self.sycomCritDmg.set(0)
        self.sycomOPS.set(0)
        for sycom in self.save_data.sycom_upgrades.sycoms:
            if sycom.id != sycom_:
                continue
            for attr in sycom.attributes:
                self.globalsetvar(attr.id[:-1], attr.bonus)
            break
        else:
            self.__createNewSycomUpgrade(sycom_)
        self.ignoreUpdateSycom = False

    def __populate_world(self):
        self.worldSeed1.set(self.save_data.world_seed1)
        self.worldSeed2.set(self.save_data.world_seed2)
        self.spawnPosX.set(self.save_data.spawn_position.x)
        self.spawnPosY.set(self.save_data.spawn_position.y)
        self.spawnPosZ.set(self.save_data.spawn_position.z)
        self.rezsRemaining.set(self.save_data.rezs_remaining)

    def __populate_vault(self):
        for (i, item) in enumerate(self.save_data.vault["items"]):
            if item.item_type[:-1] == "None":
                continue
            self.globalsetvar(f"Vault.Item{i}", item.item_type[:-1])
            #self.vaultStrings[i].set(item.item_type[:-1])

    def __populate_exe(self):
        self.exeTiers.set(self.save_data.tiers_unlocked)
        self.exeSlots.set(self.save_data.extra_slots)

    def __create_notebook(self):
        notebook = ttk.Notebook(self)
        self.characterPane = ttk.Frame(notebook)
        self.worldPane = ttk.Frame(notebook)
        self.vaultPane = ttk.Frame(notebook)
        self.exePane = ttk.Frame(notebook)
        self.lorePane = ttk.Frame(notebook)
        notebook.add(self.characterPane, text="Skins")
        notebook.add(self.worldPane, text="World")
        notebook.add(self.vaultPane, text="Vault")
        notebook.add(self.exePane, text="EXEs")
        notebook.add(self.lorePane, text="Lore")
        notebook.pack(fill=tk.BOTH, expand=True)

    def __create_menubar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open", command=self.open_bsf)
        file_menu.add_command(label="Debug", command=self.print_data)
        file_menu.add_command(label="Write", command=self.write_bsf)
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

    def __create_layout(self):
        self.__create_character_data_layout()
        self.__create_world_data_layout()
        self.__create_vault_layout()
        self.__create_exe_layout()

    def __create_character_data_layout(self):
        # set weight of grid layout so the middle grid is the largest space
        self.characterPane.grid_columnconfigure(0, weight=2)
        self.characterPane.grid_columnconfigure(1, weight=4)
        self.characterPane.grid_columnconfigure(2, weight=2)
        self.characterPane.grid_rowconfigure(0, weight=1)
        self.characterPane.grid_rowconfigure(1, weight=4)
        self.characterPane.grid_rowconfigure(2, weight=2)

        # top row, character select
        skinsFrame = tk.Frame(self.characterPane, padx=5, pady=2, bd=1, relief=tk.GROOVE)
        self.skinsFrame = skinsFrame
        openLabel = tk.Label(skinsFrame, text="Open a save file to see character data")
        openLabel.pack()

        # left frame, sycom stats
        sycomFrame = tk.Frame(self.characterPane, relief=tk.GROOVE, padx=5)
        sycomLabel = tk.Label(sycomFrame, textvariable=self.equippedSycom)
        sycomLabel.pack(fill=tk.X)
        hpFrame = tk.Frame(sycomFrame)
        hpLabel = tk.Label(hpFrame, anchor=tk.W, justify=tk.LEFT, text="HP")
        hpEntry = tk.Spinbox(hpFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomHP, width=2)
        hpLabel.pack(side=tk.LEFT, fill=tk.X)
        hpEntry.pack(side=tk.RIGHT, fill=tk.X)
        hpFrame.pack(fill=tk.X)
        #self.hpEntry = hpEntry
        battFrame = tk.Frame(sycomFrame)
        battLabel = tk.Label(battFrame, anchor=tk.W, justify=tk.LEFT, text="Battery")
        battEntry = tk.Spinbox(battFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomBattery, width=2)
        battLabel.pack(side=tk.LEFT, fill=tk.X)
        battEntry.pack(side=tk.RIGHT, fill=tk.X)
        battFrame.pack(fill=tk.X)
        #self.battEntry = battEntry
        armorFrame = tk.Frame(sycomFrame)
        armorLabel = tk.Label(armorFrame, anchor=tk.W, justify=tk.LEFT, text="Armor")
        armorEntry = tk.Spinbox(armorFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomArmor, width=2)
        armorLabel.pack(side=tk.LEFT, fill=tk.X)
        armorEntry.pack(side=tk.RIGHT, fill=tk.X)
        armorFrame.pack(fill=tk.X)
        #self.armorEntry = armorEntry
        strikeFrame = tk.Frame(sycomFrame)
        strikeLabel = tk.Label(strikeFrame, anchor=tk.W, justify=tk.LEFT, text="Strike")
        strikeEntry = tk.Spinbox(strikeFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomStrike, width=2)
        strikeLabel.pack(side=tk.LEFT, fill=tk.X)
        strikeEntry.pack(side=tk.RIGHT, fill=tk.X)
        strikeFrame.pack(fill=tk.X)
        #self.strikeEntry = strikeEntry
        blastFrame = tk.Frame(sycomFrame)
        blastLabel = tk.Label(blastFrame, anchor=tk.W, justify=tk.LEFT, text="Blast")
        blastEntry = tk.Spinbox(blastFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomBlast, width=2)
        blastLabel.pack(side=tk.LEFT, fill=tk.X)
        blastEntry.pack(side=tk.RIGHT, fill=tk.X)
        blastFrame.pack(fill=tk.X)
        #self.blastEntry = blastEntry
        stamFrame = tk.Frame(sycomFrame)
        stamLabel = tk.Label(stamFrame, anchor=tk.W, justify=tk.LEFT, text="Stam")
        stamEntry = tk.Spinbox(stamFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomStam, width=2)
        stamLabel.pack(side=tk.LEFT, fill=tk.X)
        stamEntry.pack(side=tk.RIGHT, fill=tk.X)
        stamFrame.pack(fill=tk.X)
        #self.stamEntry = stamEntry
        critChanceFrame = tk.Frame(sycomFrame)
        critChanceLabel = tk.Label(critChanceFrame, anchor=tk.W, justify=tk.LEFT, text="Crit %")
        critChanceEntry = tk.Spinbox(critChanceFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomCritChance, width=2)
        critChanceLabel.pack(side=tk.LEFT, fill=tk.X)
        critChanceEntry.pack(side=tk.RIGHT, fill=tk.X)
        critChanceFrame.pack(fill=tk.X)
        #self.critChanceEntry = critChanceEntry
        critDmgFrame = tk.Frame(sycomFrame)
        critDmgLabel = tk.Label(critDmgFrame, anchor=tk.W, justify=tk.LEFT, text="Crit Dmg")
        critDmgEntry = tk.Spinbox(critDmgFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomCritDmg, width=2)
        critDmgLabel.pack(side=tk.LEFT, fill=tk.X)
        critDmgEntry.pack(side=tk.RIGHT, fill=tk.X)
        critDmgFrame.pack(fill=tk.X)
        #self.critDmgEntry = critDmgEntry
        opsFrame = tk.Frame(sycomFrame)
        opsLabel = tk.Label(opsFrame, anchor=tk.W, justify=tk.LEFT, text="OPS")
        opsEntry = tk.Spinbox(opsFrame, from_=0, to=10, justify=tk.CENTER, textvariable=self.sycomOPS, width=2)
        opsLabel.pack(side=tk.LEFT, fill=tk.X)
        opsEntry.pack(side=tk.RIGHT, fill=tk.X)
        opsFrame.pack(fill=tk.X)
        #self.opsEntry = opsEntry

        # middle frame, character equipped gear
        gearFrame = tk.Frame(self.characterPane, relief=tk.GROOVE, padx=5)
        holoFrame = tk.Frame(gearFrame, padx=5)
        holo1Button = tk.Button(holoFrame, textvariable=self.equippedHolo1, height=4, width=8, wraplength=70)
        holo1Button.pack(side=tk.LEFT)
        holo2Button = tk.Button(holoFrame, textvariable=self.equippedHolo2, height=4, width=8, wraplength=70)
        holo2Button.pack(side=tk.LEFT)
        holo3Button = tk.Button(holoFrame, textvariable=self.equippedHolo3, height=4, width=8, wraplength=70)
        holo3Button.pack(side=tk.LEFT)
        holo4Button = tk.Button(holoFrame, textvariable=self.equippedHolo4, height=4, width=8, wraplength=70)
        holo4Button.pack(side=tk.LEFT)
        holo5Button = tk.Button(holoFrame, textvariable=self.equippedHolo5, height=4, width=8, wraplength=70)
        holo5Button.pack(side=tk.LEFT)
        holoFrame.pack(fill=tk.BOTH, expand="true")
        gearRow1Frame = tk.Frame(gearFrame, padx=5)
        sycomButton = tk.Button(gearRow1Frame, textvariable=self.equippedSycom, height=4, width=8, wraplength=70)
        sycomButton.pack(side=tk.LEFT)
        ampButton = tk.Button(gearRow1Frame, textvariable=self.equippedAmp, height=4, width=8, wraplength=70)
        ampButton.pack(side=tk.LEFT)
        gearRow1Frame.pack(fill=tk.BOTH, expand="true")
        gearRow2Frame = tk.Frame(gearFrame, padx=5)
        bladeButton = tk.Button(gearRow2Frame, textvariable=self.equippedBlade, height=4, width=8, wraplength=70)
        bladeButton.pack(side=tk.LEFT)
        railButton = tk.Button(gearRow2Frame, textvariable=self.equippedRail, height=4, width=8, wraplength=70)
        railButton.pack(side=tk.LEFT)
        disabledButton = tk.Button(gearRow2Frame, state=tk.DISABLED, height=4, width=8, wraplength=70)
        disabledButton.pack(side=tk.LEFT)
        armorButton = tk.Button(gearRow2Frame, textvariable=self.equippedArmor, height=4, width=8, wraplength=70)
        armorButton.pack(side=tk.LEFT)
        gearRow2Frame.pack(fill=tk.BOTH, expand="true")

        # right frame, item detail
        gearDetailFrame = tk.Frame(self.characterPane, bd=1, bg="#994499", relief=tk.GROOVE)

        # bottom row, global materials
        itemFrame = tk.Frame(self.characterPane, padx=5)
        bloodFrame = tk.Frame(itemFrame)
        bloodLabel = tk.Label(bloodFrame, anchor=tk.CENTER, justify=tk.CENTER, text="Bright Blood")
        bloodEntry = tk.Spinbox(bloodFrame, from_=0, to=INT32_MAX, justify=tk.CENTER, textvariable=self.itemBrightBlood)
        bloodLabel.pack(fill=tk.X)
        bloodEntry.pack(fill=tk.X)
        bloodFrame.grid(column=0, row=0)
        #self.bloodEntry = bloodEntry
        rationsFrame = tk.Frame(itemFrame)
        rationsLabel = tk.Label(rationsFrame, anchor=tk.CENTER, justify=tk.CENTER, text="Gold Rations")
        rationsEntry = tk.Spinbox(rationsFrame, from_=0, to=INT32_MAX, justify=tk.CENTER, textvariable=self.itemGoldRations)
        rationsLabel.pack(fill=tk.X)
        rationsEntry.pack(fill=tk.X)
        rationsFrame.grid(column=0, row=1)
        #self.rationsEntry = rationsEntry
        abyssFrame = tk.Frame(itemFrame)
        abyssLabel = tk.Label(abyssFrame, anchor=tk.CENTER, justify=tk.CENTER, text="Abyss Stones")
        abyssEntry = tk.Spinbox(abyssFrame, from_=0, to=INT32_MAX, justify=tk.CENTER, textvariable=self.itemAbyssStones)
        abyssLabel.pack(fill=tk.X)
        abyssEntry.pack(fill=tk.X)
        abyssFrame.grid(column=1, row=1)
        #self.abyssEntry = abyssEntry
        keysFrame = tk.Frame(itemFrame)
        keysLabel = tk.Label(keysFrame, anchor=tk.CENTER, justify=tk.CENTER, text="Keys")
        keysEntry = tk.Spinbox(keysFrame, from_=0, to=INT32_MAX, justify=tk.CENTER, textvariable=self.itemKeys)
        keysLabel.pack(fill=tk.X)
        keysEntry.pack(fill=tk.X)
        keysFrame.grid(column=2, row=0)
        #self.keysEntry = keysEntry
        coresFrame = tk.Frame(itemFrame)
        coresLabel = tk.Label(coresFrame, anchor=tk.CENTER, justify=tk.CENTER, text="Cores")
        coresEntry = tk.Spinbox(coresFrame, from_=0, to=INT32_MAX, justify=tk.CENTER, textvariable=self.itemCores)
        coresLabel.pack(fill=tk.X)
        coresEntry.pack(fill=tk.X)
        coresFrame.grid(column=2, row=1)
        #self.coresEntry = coresEntry
        partCoresFrame = tk.Frame(itemFrame)
        partCoresLabel = tk.Label(partCoresFrame, anchor=tk.CENTER, justify=tk.CENTER, text="Partial Cores")
        partCoresEntry = tk.Spinbox(partCoresFrame, from_=0, to=3, justify=tk.CENTER, textvariable=self.itemPartialCores)
        partCoresLabel.pack(fill=tk.X)
        partCoresEntry.pack(fill=tk.X)
        partCoresFrame.grid(column=2, row=2)
        #self.partCoresEntry = partCoresEntry
        materialsFrame = tk.Frame(itemFrame)
        materialsLabel = tk.Label(materialsFrame, anchor=tk.CENTER, justify=tk.CENTER, text="Materials")
        materialsEntry = tk.Spinbox(materialsFrame, from_=0, to=INT32_MAX, justify=tk.CENTER, textvariable=self.itemMaterials)
        materialsLabel.pack(fill=tk.X)
        materialsEntry.pack(fill=tk.X)
        materialsFrame.grid(column=1, row=0)
        #self.materialsEntry = materialsEntry

        # put frames on grid
        skinsFrame.grid(column=0, row=0, columnspan=3, sticky="nsew")
        sycomFrame.grid(column=0, row=1, rowspan=2, sticky="nsew")
        gearFrame.grid(column=1, row=1, sticky="nsew")
        gearDetailFrame.grid(column=2, row=1, rowspan=2, sticky="nsew")
        itemFrame.grid(column=1, row=2, sticky="nsew")

    def __create_world_data_layout(self):
        seed1Label = tk.Label(self.worldPane, anchor=tk.CENTER, justify=tk.LEFT, text="Seed1")
        seed1Entry = tk.Spinbox(self.worldPane, textvariable=self.worldSeed1, from_=INT32_MIN, to=INT32_MAX)
        seed2Label = tk.Label(self.worldPane, anchor=tk.CENTER, justify=tk.LEFT, text="Seed2")
        seed2Entry = tk.Entry(self.worldPane, textvariable=self.worldSeed2)
        seed1Label.pack()
        seed1Entry.pack()
        seed2Label.pack()
        seed2Entry.pack()
        spawnPosXLabel = tk.Label(self.worldPane, anchor=tk.CENTER, justify=tk.LEFT, text="Spawn.X")
        spawnPosXEntry = tk.Entry(self.worldPane, textvariable=self.spawnPosX)
        spawnPosYLabel = tk.Label(self.worldPane, anchor=tk.CENTER, justify=tk.LEFT, text="Spawn.Y")
        spawnPosYEntry = tk.Entry(self.worldPane, textvariable=self.spawnPosY)
        spawnPosZLabel = tk.Label(self.worldPane, anchor=tk.CENTER, justify=tk.LEFT, text="Spawn.Z")
        spawnPosZEntry = tk.Entry(self.worldPane, textvariable=self.spawnPosZ)
        spawnPosXLabel.pack()
        spawnPosXEntry.pack()
        spawnPosYLabel.pack()
        spawnPosYEntry.pack()
        spawnPosZLabel.pack()
        spawnPosZEntry.pack()
        rezsLabel = tk.Label(self.worldPane, anchor=tk.CENTER, justify=tk.LEFT, text="Rezs Remaining")
        rezsEntry = tk.Spinbox(self.worldPane, textvariable=self.rezsRemaining, from_=0, to=4)
        rezsLabel.pack()
        rezsEntry.pack()

    def __create_vault_layout(self):
        # left frame, vault items
        vaultFrame = tk.Frame(self.vaultPane, padx=5, pady=5, bd=1, relief=tk.GROOVE)
        self.vaultItems = []
        self.vaultStrings = []
        for i in range(0, 26):
            bStr = tk.StringVar(self, name=f"Vault.Item{i}")
            button = tk.Button(vaultFrame, textvariable=bStr, height=4, width=8, wraplength=70)
            #button = tk.Menubutton(vaultFrame, textvariable=bStr, height=4, width=8, wraplength=70, relief=tk.RAISED, bd=1)
            #menu = tk.Menu(button, tearoff=False)
            #menu.add_command(label="Move")
            #menu.add_command(label="Copy")
            #button.config(menu=menu)
            gx = i // 4
            gy = i % 4
            button.grid(column=gy, row=gx)
            self.vaultItems.append(button)
            self.vaultStrings.append(bStr)
        # right frame, item detail
        gearDetailFrame = tk.Frame(self.vaultPane, bd=1, bg="#994499", relief=tk.GROOVE)
        vaultFrame.pack(fill=tk.BOTH, side=tk.LEFT)
        gearDetailFrame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    def __create_exe_layout(self):
        exeFrame = tk.Frame(self.exePane, padx=5, pady=5)
        tk.Label(exeFrame, text="Tiers Unlocked").grid(column=0, row=0)
        tk.Spinbox(exeFrame, textvariable=self.exeTiers, from_=0, to=6).grid(column=1, row=0)
        tk.Label(exeFrame, text="Extra Slots Unlocked").grid(column=0, row=1)
        tk.Spinbox(exeFrame, textvariable=self.exeSlots, from_=0, to=19).grid(column=1, row=1)
        exeFrame.pack(fill=tk.BOTH)



Application().run()
