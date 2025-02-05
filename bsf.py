import pathlib
import struct
import zlib
from construct import *

Unreal_header = Struct(
    "magic" / Int64ub,
    "a" / Int64ub,
)
Compressed_info = Struct(
    "compressed_size" / Int64ul,
    "decompressed_size" / Int64ul
)
BSF = Struct(
    "header" / Unreal_header,
    "data_size" / Compressed_info,
    "dup" / Compressed_info,
    "data" / Array(this.data_size.compressed_size, Byte)
)

def read_bsf(path):
    with path.open('rb') as f:
        bsf = f.read()
    bsf = BSF.parse(bsf)
    #header = Unreal_header.parse(bsf[0:16])
    #compressed_size = Compressed_info.parse(bsf[16:32])
    #dup = Compressed_info.parse(bsf[32:48])
    #data = bsf[48:]
    return bsf

def deflate_data(data):
    return zlib.decompress(data)

def compress_save(save):
    return zlib.compress(save)

def write_bsf(path, data):
    unreal_header = b'\xC1\x83\x2A\x9E\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00'
    comp = compress_save(data)
    comp_size = len(comp)
    decomp_size = len(data)
    path.write_bytes(
        unreal_header +
        struct.pack('<q', comp_size) +
        struct.pack('<q', decomp_size) +
        struct.pack('<q', comp_size) +
        struct.pack('<q', decomp_size) +
        comp
    )
    return 0

FName = PascalString(Int32ul, "utf8")
UnknownStruct = Struct(
    "a" / Int32ul,
    "b" / Int32ul,
    "c" / Int32ul,
    "d" / Int32ul,
    "e" / Int32ul,
    "str1" / FName,
    "str2" / FName,
    "p" / Int8ul,
    "q" / Int32ul
)
UnknownStruct17Data = Struct(
    "a" / Int8ul,
    "d" / Int32sl
)
UnknownStruct17 = Struct(
    "length" / Int32ul,
    "a" / Int32ul,
    "data" / Array(this.length, UnknownStruct17Data)
)
UnknownStruct18 = Struct(
    "length" / Int32ul,
    "strings" / Array(this.length, FName)
)
UnknownStruct24 = Struct(
    "length" / Int32ul,
    "data" / Array(this.length, Int32ul),
    "ex" / Int32ul
)
EXE_Mod = Struct(
    "mod" / FName,
    "count" / Int32ul
)
EXEsArray = Struct(
    "length" / Int32ul,
    "mods" / Array(this.length, EXE_Mod)
)
CharacterIDArray = Struct(
    "length" / Int32ul,
    "characters" / Array(this.length, FName)
)
Gear_Data = Struct(
    "id" / FName,
    "data" / Array(5, Int32ul),
    "none" / FName,
    "dup" / FName,
    "pad" / Int8ul
)
GearArray = Struct(
    "length" / Int32ul,
    "gear" / Array(this.length, Gear_Data)
)
Item_Mod = Struct(
    "mod_type" / FName,
    "data" / Int32ul
)
Item = Struct(
    "six" / Int32ul,
    "data" / Array(4, Int32ul),
    "item_id" / FName,
    "level" / Int32ul,
    "rarity" / Int32ul,
    "a" / Int32ul,
    "item_type" / Int8ul,
    "b" / Int8ul,
    "atk_min" / Float32l,
    "c" / Int8ul,
    "atk_max" / Float32l,
    "rate_of_fire" / Float32l,
    "d" / Int32ul,
    "d_d" / Int8ul,
    "num_mods" / Int32ul,
    "mods" / Array(this.num_mods, Item_Mod),
    "v" / Int32ul,
    "x" / Int8ul,
    "stagger_min" / Float32l,
    "y" / Int8ul,
    "stagger_max" / Float32l,
    "six2" / Int32ul,
    "attribute" / FName,
    "attribute_bonus" / Float32l,
    "armor_type" / Int8ul,
    "hp" / Int32sl,
    "armor" / Int32sl,
    "dash_speed" / Int32sl,
    "dash_distance" / Int32sl,
    "global_id" / Int32ul,
    "z" / Int8ul,
    "durability" / Int32ul
)
Character_Equipment = Struct(
    "character" / FName,
    "two" / Int32ul,
    "equipped_sycom" / FName,
    "length" / Int32ul,
    "equipment" / Array(this.length, Struct("slot" / Int8ul, "item" / Item))
)
CharacterItemArray = Struct(
    "length" / Int32ul,
    "characters" / Array(this.length, Character_Equipment)
)
Vec3 = Struct(
    "x" / Float32l,
    "y" / Float32l,
    "z" / Float32l
)
POI = Struct(
    "poi_type" / FName,
    "position" / Vec3,
    "a" / Int32ul,
    "s" / Int8ul,
    "b" / Int32ul,
    "t" / Int8ul,
    "hex" / FName,
    "type2" / FName,
    "biome" / FName,
    "f" / Int32ul
)
World_POIs = Struct(
    "length" / Int32ul,
    "pois" / Array(this.length, POI)
)
Vault = Struct(
    "length" / Int32ul,
    "items" / Array(this.length, Item)
)
Quests = Struct(
    "length" / Int32ul,
    "quests" / Array(this.length, Struct("a" / Int32ul, "id" / FName, "b" / Int32ul))
)
Vendors = Struct(
    "length" / Int32ul,
    "vendors" / Array(this.length, Struct("vendor_type" / FName, "a" / Int32ul, "length" / Int32ul, "inventory" / Array(this.length, Struct("a" / Int32ul, "item" / Item, "b" / Int32sl, "c" / Int32sl))))
)
AttributeBonus = Struct(
    "id" / FName,
    "bonus" / Int32ul
)
Sycom = Struct(
    "id" / FName,
    "length" / Int32ul,
    "attributes" / Array(this.length, AttributeBonus)
)
SycomUpgrades = Struct(
    "length" / Int32ul,
    "sycoms" / Array(this.length, Sycom)
)
HLB_Save = Struct(
    "length" / Int32ul,
    "unknown1" / Int32ul,
    "unknown2" / Int32ul,
    "unknown3" / Int32ul,
    "bright_blood" / Int32sl,
    "unknownA" / UnknownStruct,
    "unknownB" / UnknownStruct,
    "unknown4" / Int32ul,
    "abyss_stones" / Int32sl,
    "gold_rations" / Int32sl,
    "unknown5" / Array(7, Int32sl),
    "cores" / Int32sl,
    "partial_cores" / Int32sl,
    "medigems_old" / Int32sl,
    "unknown6" / Array(2, Int32sl),
    "materials" / Int32sl,
    "unknown7" / Array(2, Int32sl),
    "keys" / Int32sl,
    "unknown8" / Array(4, Int32sl),
    "some_id" / Int32ul,
    "unknown9" / Array(4, Int32sl),
    "unlocked_exes" / EXEsArray,
    "tiers_unlocked" / Int32sl,
    "unsure_purpose_exes" / EXEsArray,
    "extra_slots" / Int32sl,
    "equipped_exes" / EXEsArray,
    "difficulty" / Int32ul,
    "total_runs" / Int32ul,
    "unknown10" / Array(3, Int32ul),
    "unknown11" / Float32l,
    "unlocked_characters" / CharacterIDArray,
    "unknown12" / Int32ul,
    "gear_stuff" / GearArray,
    "unknown13" / Array(2, Int32ul),
    "none_array" / Array(19, FName),
    "unknown14" / Int32ul,
    "active_character" / FName,
    "equipped_items" / CharacterItemArray,
    "unknown15" / Array(10, Int32ul),
    "world_seed1" / Int32ul,
    "world_seed2" / Int32ul,
    "unknown16" / Int32ul,
    "spawn_position" / Vec3,
    "unknown17" / UnknownStruct17,
    "unknown18" / UnknownStruct18,
    "some_string" / FName,
    "unknown19" / Int32ul,
    "unknown20" / Int8ul,
    "current_cycle_run_count" / Int32ul,
    "unknown21" / Int32ul,
    "rank_maybe" / Int32ul,
    "world_pois" / World_POIs,
    "unknown22" / Array(3, Int32ul),
    "rezs_remaining" / Int32ul,
    "unknown23" / Array(2, Int32ul),
    "unknown24" / UnknownStruct24,
    "vault" / Vault,
    "unknown25" / Int32ul,
    "lore_fragments_found" / Struct(
        "length" / Int32ul,
        "fragments" / Array(this.length, FName)
        ),
    "lore_unlocked" / Struct(
        "length" / Int32ul,
        "scenes" / Array(this.length, FName)
        ),
    "unknown26" / Array(2, Int32ul),
    "quests" / Quests,
    "unknown27" / Array(4, Int32ul),
    "vendor_unknown1" / Struct(
        "length" / Int32ul,
        "vendors" / Array(this.length, Struct("id" / FName, "a" / Int32ul, "s" / Int8ul, "b" / Int32ul))
        ),
    "vendor_upgrades" / Struct(
        "length" / Int32ul,
        "vendors" / Array(this.length, Struct("id" / FName, "gifts" / Int32ul))
        ),
    "vendor_stock" / Struct(
        "length" / Int32ul,
        "vendors" / Array(this.length, Struct("id" / FName, "a" / Int32ul, "length" / Int32ul, "items" / Array(this.length, Item)))
        ),
    "vendor_unknown2" / Struct(
        "length" / Int32ul,
        "vendors" / Array(this.length, Struct("id" / FName, "a" / Int32ul, "b" / Int32sl, "c" / Int32ul, "d" / Int32ul))
        ),
    "unknown28" / Int32ul,
    "sycoms_unlocked" / Struct(
        "length" / Int32ul,
        "sycoms" / Array(this.length, FName)
        ),
    "unknown29" / Int32ul,
    "sycom_upgrades" / SycomUpgrades,
    "unknown30" / Array(2, Int32ul),
    "starting_gear" / Struct(
        "length" / Int32ul,
        "characters" / Array(this.length, Struct("sycom" / FName, "length" / Int32ul, "items" / Array(this.length, Struct("id" / FName, "item" / Item))))
        ),
    "unknown31" / Int32ul,
    "tutorials" / Struct(
        "length" / Int32ul,
        "tutorials" / Array(this.length, FName)
        ),
    "unknown32" / Int32ul,
    "world_vendors" / Vendors,
    "unknown33" / Array(25, Int32ul),
    "pad" / Int8ul
)

def generate_save_struct(data):
    return HLB_Save.parse(data)

def generate_save_bytes(save):
    raw = HLB_Save.build(save)
    length = len(raw) - 4
    new_length = Int32ul.build(length)
    return new_length + raw[4:]
