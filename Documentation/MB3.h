// MB3 files reflect changes in Energy Pulse output
// MB3.h Nov 9 2010 
// Sept 2 2010 Added unit conversions
// Aug 27 2010 Put all congiguration parameters in a CONFI_TYPE struct
// MB1.h April 21 2010. Include file for MB1.c,
// first Modbus attempt with PIC16F1936

//	This source code is confidential to Clark Solutions, Hudson Ma
// and may not be used for any purpose without written consent from Clark Solutions.
// Clark Solutions US Flow meter
// Author: Jack Zettler Teconex inc

//#include <pic.h>

void		interrupt isr(void);		//Single interrupt service
void		init_1936(void);			//Initializes controller
void		init_defaults(void);		//Initializes all non-comm parameters
void		init_comm();				//Sets communication parameters
void		get_su(void);				//Update set up parameters
void		delay(uint16);				//General purpose program delay
void		measure(void);				//Get RTD and flow raw data
double	pulse_out_type(void);	//Decides what Pulse output should be
void		reply(void);				//Compose MB reply
void		vett(void);					//Qualify message
void		process(void);				//Process message
void		build_read_resp(byte fc);	//Constructs response packet
void		write_word(byte fc);			//Writes to holding registers
void		fc_err(void);				//Handles fc errors
uint16	get_rtd(byte loc);		//A/D counts
void 		cal_rtd(void);				//Calibrate RTD circuit		
double	calc_temps(void);			//Determine temps and density
double	calc_r(double rho, double sigma, double mx);
double	calc_r_p(double *rho, double *sigma, double *mx);
void		set_Fout(double freq);	//Set output pulse frequency
void		write_eeprom_double(byte d_add, double d_data);//Write double data to EEPROM	
void		write_eeprom_int(byte d_add, byte hi, byte lo);//Write uint16 data to EEPROM
void		read_double(double *src, byte *dest);
double	read_eeprom_double(byte d_add);	//Retrieve EEPROM data
uint16	read_eeprom_int(byte add);		//Retrieve uint16 from EEPROM
uint16	CRC16(byte *p, uint16 length);

#define	PB(adr,bit)			@((unsigned)(&adr)*8 + (bit))

typedef struct          //Communication flags
{
 byte 	frame			:1;	//Reply  
 byte  	fc_err		:1;	//Reply
 byte		err			:1;	//Set hi if comm error
 byte		tx				:1;	//Hi while transmitting
 byte		rx				:1;	//Hi while receiving
 byte		for_us		:1;	//Not our address
 byte		nine			:1;	//Ninth bit
 byte		config		:1;	//Setup if 1
} COMM_TYPE;
typedef	struct
{
 byte	done			:1;
 byte	rtd			:1;
 byte	loflo			:1;
 byte	unused		:5;
}MEAS_TYPE;

typedef struct
{
 byte		freq_type;			//Flow or energy for pulse output
 byte		q;						//Flow rate units;
 byte		e;						//Energy rate units;
 byte		m;						//Mass rate units, lbs/m or kg/m
 byte		qs;					//Flow storage units
 byte		es;					//Energy storage units
 byte		ms;					//Mass storage units
 byte		config;				//Commissioning or run mode
}CONFIG_TYPE;

enum	{Q_rate, E_rate, M_rate, Q_tot, E_tot, M_tot, Temp_loc, Temp_rem};

enum	{G_MIN, L_MIN, L_SEC, BTU_MIN, KBTU_MIN, KBTU_HR, KW, LBS_MIN, KG_MIN,
			GS, LS, M3S, KBTU, KWHR, TONHR,  LB, KG};

										//	Unit conversion factors
//							  G_MIN(0)	L_MIN(1)  L_SEC(2)  BTU_MIN(3) KBTU_MIN(4)	KBTU_HR(5)	KW(6)	  LBS/M(7)		
const double Conv[17] = {1.0,   3.785412,	 . 06308,    1.0,			.001,	 	    .06, 	  .01758, 	1.0,	 
		//	 KG_MIN(8)		GS(9) LS(10)   	M3S(11)	KBTU(12)	 KWHR(13)	TONHR(14) LB(15) 	KG(16)	 
			 3.785412,		 1	, 3.785412,	 .003785412, .001 ,  .293297,	  83.333e-6, 	 1, 	.45359 };

// Coefficients to determine density from temp. 
const double	Cal_rho[3] = {-8.047e-5,4.028e-3, 62.402};
	
	
#define	MAX_COMM_BUF		15			//Max allowed size of Comm buffer
#define	MAX_REPLY_BUF		64			//Maximum size of reply packet
#define	BASE_READ_REGS		0			//Logical address of first read register
#define	BASE_WRITE_REGS	100		//Logical address of first write register
#define	BASE_COIL_REGS		0			//Logical address of first write register
#define	BASE_COMM_REGS		200		//Base of communication parameters regs
#define	BASE_FAC_REGS		300		//Base of K, Dz regs
#define	MAX_READ_REGS		14			//Max number of registers to read
#define	MAX_WRITE_REGS		8			//Max number of operational write regs
#define	MAX_COIL_REGS		5			//Max number of coils
#define	MAX_COMM_REGS		4			//Max number of communication regs
#define	MAX_FAC_REGS		2			//Max number of factory regs
#define	BAD_DATA_ADD		0x02		//Illegal range requested, Ex code 02
#define	BAD_DATA_RANGE		0x03		//Illegal range requested, Ex code 02
#define	BAD_FC				0x01		//Unsupported FC
#define	SETU_ADD				0x01		//Address to use when setting up
#define	CLK_FREQ				8.0		//MHz	
#define	TIME_BASE			.004402	//Convert Rt_ints to minutes, measured 7-27-10
#define	T0_OFFSET			50			//Empirically determined
#define	FLOW_PW				15			//Tmr2 ints for 2 ms pulse width
#define	ENERGY_PW			3915		//Tmr2 ints for 5 ms pulse width
#define	CONSTK				15.6006	//Rtd calc constant
#define	CONSTR				3.1001	//Rtd calc constant	
#define	RA						5000.0	//Ra value for RTD calc
#define	MIN_INTS				20			//Minimum interrupts in 2 sec period for Huba flow
#define	SETUP_BR				0x00		//Select 9600
#define	SETUP_PARITY		0x00		//Select no parity
#define	SPBRGL96				0xCF		//For 9600, 207
#define	SPBRGL19				0x67		//For 19.2KB, 103
#define	CONFIG_FAC			0x00		//Doing factory set up
#define	CONFIG_COMM			0x01		//Change comm parameters only
#define	CONFIG_SU			0x03		//Update set up perameters
#define	CONFIG_DONE			0x04		//Config has been updated

//EEDATA Adresses

#define	TOTAL_BASE			0x10			//Base of totalized values	and rates
		
#define	F_TOTAL_ADD			0x00			//Stored Energy Total
#define	E_TOTAL_ADD			0x04			//Stored Flow total
#define	M_TOTAL_ADD			0x08			//Stored Mass total

#define	COIL_BASE			0x18		

#define	SELECTP_ADD			0x00			//Pulse output. 0x00 for Energy,0xFF for Flow
#define	SELECTT_ADD 		0x02			//Temperature units. 0x00 for C, 0xFF for F

#define	OP_BASE				0x20			//Base address of first setup write register

#define	Q_UNITS_ADD			0x00			//Flow rate units
#define	E_UNITS_ADD			0x02			//Energy rate units
#define	M_UNITS_ADD			0x08			//Mass rate units
#define	QS_UNITS_ADD		0x04			//Flow total units
#define	ES_UNITS_ADD		0x06			//Flow total units
#define	MS_UNITS_ADD		0x08			//Mass total units


#define	COMM_BASE			0x40			//Base address of first comm register

#define	ID_ADD				0x00			//Our Slave ID
#define	BR_ADD				0x02			//Baud Rate
#define	PARITY_ADD			0x04			//Parity selection

#define	DZ_ADD				0x00			//Store DZ
#define	K_ADD					0x04			//Store K

//End of EEDATA Adresses		

//States
#define	Idle					0x00			//State assignments
#define	Vett					0x01
#define	Process				0x02			
#define	Reply					0x03
#define	Update				0x04			


// TRIS Assignments 

#define TRISA_ALL    0XBD		//All input ecept CLKOUT and FAULT
#define TRISB_ALL    0XD9		//Port B is Int input,out on 1,2,5, RB.6,.7 for ICSP
#define TRISC_ALL	   0X80		//6 Fet selects for temp, Tx out and RX in
#define WPUB_INIT		0x0C		//Weak pull ups on commissioning inputs

#define	T09615		25			//TMR0 presets for T.15 and T3.5 times for
#define	T09635		50			// 9600 and 19.2KBrates
#define 	T01915		23
#define	T01935		54

//Port assignments

static bit   FAULT		PB(PORTA,1);  	//Commission in debug mode
static bit   HUBA_INT	PB(PORTB,0);   //UFO int
static bit   TXENB		PB(PORTB,1);   //Transmitter enable
static bit   RXENB		PB(PORTB,2);   //Receive enable
static bit   CONFIGR		PB(PORTB,3);   //Commissioning pin,debug
static bit   CONFIGD		PB(PORTB,4);   //Commissioning pin,release
static bit   PULSE		PB(PORTB,5);   //Pulse output
static bit   DEC		   PB(PORTB,6);   //Cal dec dc
static bit   INC			PB(PORTB,7);   //Cal inc dc



//Port C is temperature selects plus TX, RX

static bit   RTDR1	   PB(PORTC,0);   //First remote RTD common
static bit   RTDR2	   PB(PORTC,1);   //Second remote RTD common
static bit   RTDL	   	PB(PORTC,2);   //Local RTD common
static bit   REF15	   PB(PORTC,3);   //1500 ohm reference
static bit   REF10	   PB(PORTC,4);   //1000 ohm reference
static bit   SPARE	   PB(PORTC,5);   //Unused FET switch
static bit   TX		   PB(PORTC,6);   //Tx output
static bit   RX			PB(PORTC,7);   //Rx input
//RC6, RC7 are UART functions

//Register initialization defines
#define	OSCCON_INIT		0x72	//PPL disenabled, clk freq 8 MHz
#define  INTCON_INIT		0xD0 	//GIE,PEIE, INTE enabled
#define	RCSTA_INIT		0x90	//SPEN, CREN set only
#define	PORTB_INIT		0xF4	//TXENB off (hi), RXENB on, (low)
#define	ANSELB_INIT		0x00	//PortB pins are all I/O
#define  OPTION_INIT 	0x45 	//Pullups,TMR0 Focs/4,prescale = 1:64,TMR0
#define	ADCON0_INIT		0x01	//Chan 0, AD is ON 
#define	ADCON1_INIT		0xA0	//Vdd/Vss ref,FOSC 32 TAD, and rt justified
#define	ANSELA_INIT		0x01	//RA0 is analog pin
#define	T6CON_INIT		0x07	//Prescaler = 64, ON
#define	T1CON_INIT		0x31	//Fosc/4 and prescale = 8,TMR1 on
#define  T2CON_INIT 	 	0x00 	//Prescale= Postscale = 1:1, TMR2 Off
#define	T4CON_INIT		0x00	//
#define	CHAN0				0x01	//Chan 0
#define	CCP1CON_DATA	0x00	//Disable PWM
//#define	CCP1CON_PWM		0x0C	//Enable PWM, LSBs are 0
//#define	EECON1_INIT		0x00	//Disable all EEPROM Reads/Writes



static const uint16 wCRCTable[] = {
   0X0000, 0XC0C1, 0XC181, 0X0140, 0XC301, 0X03C0, 0X0280, 0XC241,
   0XC601, 0X06C0, 0X0780, 0XC741, 0X0500, 0XC5C1, 0XC481, 0X0440,
   0XCC01, 0X0CC0, 0X0D80, 0XCD41, 0X0F00, 0XCFC1, 0XCE81, 0X0E40,
   0X0A00, 0XCAC1, 0XCB81, 0X0B40, 0XC901, 0X09C0, 0X0880, 0XC841,
   0XD801, 0X18C0, 0X1980, 0XD941, 0X1B00, 0XDBC1, 0XDA81, 0X1A40,
   0X1E00, 0XDEC1, 0XDF81, 0X1F40, 0XDD01, 0X1DC0, 0X1C80, 0XDC41,
   0X1400, 0XD4C1, 0XD581, 0X1540, 0XD701, 0X17C0, 0X1680, 0XD641,
   0XD201, 0X12C0, 0X1380, 0XD341, 0X1100, 0XD1C1, 0XD081, 0X1040,
   0XF001, 0X30C0, 0X3180, 0XF141, 0X3300, 0XF3C1, 0XF281, 0X3240,
   0X3600, 0XF6C1, 0XF781, 0X3740, 0XF501, 0X35C0, 0X3480, 0XF441,
   0X3C00, 0XFCC1, 0XFD81, 0X3D40, 0XFF01, 0X3FC0, 0X3E80, 0XFE41,
   0XFA01, 0X3AC0, 0X3B80, 0XFB41, 0X3900, 0XF9C1, 0XF881, 0X3840,
   0X2800, 0XE8C1, 0XE981, 0X2940, 0XEB01, 0X2BC0, 0X2A80, 0XEA41,
   0XEE01, 0X2EC0, 0X2F80, 0XEF41, 0X2D00, 0XEDC1, 0XEC81, 0X2C40,
   0XE401, 0X24C0, 0X2580, 0XE541, 0X2700, 0XE7C1, 0XE681, 0X2640,
   0X2200, 0XE2C1, 0XE381, 0X2340, 0XE101, 0X21C0, 0X2080, 0XE041,
   0XA001, 0X60C0, 0X6180, 0XA141, 0X6300, 0XA3C1, 0XA281, 0X6240,
   0X6600, 0XA6C1, 0XA781, 0X6740, 0XA501, 0X65C0, 0X6480, 0XA441,
   0X6C00, 0XACC1, 0XAD81, 0X6D40, 0XAF01, 0X6FC0, 0X6E80, 0XAE41,
   0XAA01, 0X6AC0, 0X6B80, 0XAB41, 0X6900, 0XA9C1, 0XA881, 0X6840,
   0X7800, 0XB8C1, 0XB981, 0X7940, 0XBB01, 0X7BC0, 0X7A80, 0XBA41,
   0XBE01, 0X7EC0, 0X7F80, 0XBF41, 0X7D00, 0XBDC1, 0XBC81, 0X7C40,
   0XB401, 0X74C0, 0X7580, 0XB541, 0X7700, 0XB7C1, 0XB681, 0X7640,
   0X7200, 0XB2C1, 0XB381, 0X7340, 0XB101, 0X71C0, 0X7080, 0XB041,
   0X5000, 0X90C1, 0X9181, 0X5140, 0X9301, 0X53C0, 0X5280, 0X9241,
   0X9601, 0X56C0, 0X5780, 0X9741, 0X5500, 0X95C1, 0X9481, 0X5440,
   0X9C01, 0X5CC0, 0X5D80, 0X9D41, 0X5F00, 0X9FC1, 0X9E81, 0X5E40,
   0X5A00, 0X9AC1, 0X9B81, 0X5B40, 0X9901, 0X59C0, 0X5880, 0X9841,
   0X8801, 0X48C0, 0X4980, 0X8941, 0X4B00, 0X8BC1, 0X8A81, 0X4A40,
   0X4E00, 0X8EC1, 0X8F81, 0X4F40, 0X8D01, 0X4DC0, 0X4C80, 0X8C41,
   0X4400, 0X84C1, 0X8581, 0X4540, 0X8701, 0X47C0, 0X4680, 0X8641,
   0X8201, 0X42C0, 0X4380, 0X8341, 0X4100, 0X81C1, 0X8081, 0X4040 };

