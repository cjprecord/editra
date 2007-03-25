-- Uncomment the following lines to use the declarations that are
-- provided for instantiating Xilinx primitive components.
--library UNISIM;
--use UNISIM.VComponents.all;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.NUMERIC_STD.ALL; 

entity inrom is
Port ( en : in std_logic;
clk : in std_logic;
dout : out std_logic_vector( 15 downto 0);--16 bit data that needs to
be input to the system
valid : out std_logic; --Tells that valid data is present on output
reset : in std_logic
);
end inrom;

architecture rtl of inrom is

type array_rom is array (31 downto 0) of std_logic_vector( 15 downto
0);
signal myarray : array_rom;
signal valid_sig:std_logic;
signal dout_sig : std_logic_vector(15 downto 0);
signal clk2: std_logic;

begin

myarray(0) <= x"0000";
myarray(1) <= x"0000";
myarray(2) <= x"0000";
myarray(3) <= x"003C";
myarray(4) <= x"0000";
myarray(5) <= x"0000";
myarray(6) <= x"0064";
myarray(7) <= x"0000";
myarray(8) <= x"0000";
myarray(9) <= x"000A";
myarray(10) <= x"0000";
myarray(11) <= x"0000";
myarray(12) <= x"003C";
myarray(13) <= x"0000";
myarray(14) <= x"0000";
myarray(15) <= x"0064";
myarray(16) <= x"0000";
myarray(17) <= x"0000";
myarray(1Cool <= x"0046";
myarray(19) <= x"0000";
myarray(20) <= x"0000";
myarray(21) <= x"006E";
myarray(22) <= x"0000";
myarray(23) <= x"0000";
myarray(24) <= x"000A";
myarray(25) <= x"0000";
myarray(26) <= x"0000";
myarray(27) <= x"0046";
myarray(2Cool <= x"0000";
myarray(29) <= x"0000";
myarray(30) <= x"006E";
myarray(31) <= x"0000";

process( reset,clk)
variable romvar:natural range 0 to 31;
--variable incr: boolean;

begin



if reset = '1' then
dout_sig <= (others=>'0');
valid_sig <='0';
romvar :=0;



elsif (clk'event and clk='1') then
if en='1' then

dout_sig <= myarray (romvar);
valid_sig<='1';
romvar :=romvar + 1;

else
dout_sig <= myarray (romvar);
valid_sig<='0'; 