// MB3 files reflect changes in Energy Pulse output
// MB3.c Nov 9 2010. Compile with Ver 9.80 only
// Additions will be made for units, media, and density corrections.
//	Sept 2 2010 All unit functions seem to work. This is a keeper
// Implemented flow and energy units and selection
//	First file to implement ModBus with a Pic16F1936 processor. 
//	As of 7-14-10, project is compiled with Ver 9.71a

#include	<htc.h>					//Header file for Microchip processors
#include	"mbdefs.h"
#include	"mb3.h"	               
#include	<stdio.h>
#include	<stdlib.h>
#include	<math.h>

#define	_SET_UP

__CONFIG(FOSC_INTOSC & WDTE_OFF & PWRTE_OFF & MCLRE_ON & CP_OFF & CPD_OFF & BOREN_OFF 
			& CLKOUTEN_ON & IESO_OFF & FCMEN_OFF);

__CONFIG(WRT_OFF & VCAPEN_OFF & PLLEN_OFF & STVREN_OFF & BORV_25  & LVP_OFF); //9.80

#define	_H34		//Define if for 3/4 meter
//#define	_H12	//if for 1/2 meter
byte				Comm_buf[MAX_COMM_BUF]; //Receive buffer
byte				Reply_buf[MAX_REPLY_BUF];//Reply buffer
uint16			Counts[5];					//Array to hold A/D values from temperature measurements
double			Read_regs[MAX_READ_REGS];//Modbus holding registers for readable variables
double			ConvQ, ConvE,ConvQS, ConvES;	//Unit conversions,assigned in init_comm()
byte				*Buf_ptr;					//Pointer to Rx/Tx  buffer
COMM_TYPE		Comm;							//Comm flags
MEAS_TYPE		Meas;							//Measurement flags
CONFIG_TYPE		Config;						//Holds all configuration parameters
volatile byte	Dummy;						//Temp variable for debug only.
byte				State;						//Current activity
byte				My_add;						//Our Modbus address
byte				Length;						//Length of communication buffers,Coom, Reply etc
uint16			NTau1,Nl;					//Timer 2 long count for pulse frequency output.
byte				NTau2,Ns;					//Timer 2 short count
double			FreqOut;						//Output frequency
double			FreqH;						//Huba frequency
byte				Pulse_width;				//Set width of pulse output
uint16			Q_time, Q_ints;			//Accumulated time and HUBA pulses
uint16			Rt_ints;						//Count of Tmr1 interrupts to structure real time clock
byte				Tmr2_ticks;					//Used for pulse width timing
uint16			N_meas;						//Number of 2 sec measurement taken
double			Rho, Sigma;					//Cal constants for RTD calculation
byte				Rx_char;						//Received character for parity checking
byte				Parity, Sel_parity;		//None, Odd, Even parity

main()
{
byte *ptr;

init_1936();
if(!CONFIGD || !CONFIGR )			//If programming config request is low, 
	{
	init_comm();						//Writes ID, Baud rate and parity to EEPROM
	Config.config = CONFIG_COMM;			//Set to test later
	}
if(!CONFIGD)							//Factory setup
	init_defaults();					//set default set up and comm parameters
while(!CONFIGD);						//Wait for button release 		
FAULT = (FAULT)? OFF : ON;	//Toggle pulse output
ptr = (byte*)&Meas;						//Clear all flags
*ptr = 0x00;
cal_rtd();									//Calibrate RTD circuit
TMR0 = 0;
do
	Dummy = RCREG;
while(RCIF || (TMR0 < 200));			//Read until link is idle
State = Idle;								//Test reply code
RCIE = ON;
Comm.frame = Comm.fc_err =  Comm.err = 0;//Zero all comm flags
Buf_ptr = Comm_buf;
Rt_ints = N_meas = 0;					//Reset totalizer routines
//	write_eeprom_double(TOTAL_BASE + F_TOTAL_ADD, 0.0);		//Debug only
//	write_eeprom_double(TOTAL_BASE + E_TOTAL_ADD, 0.0);

while(1)
	{
	if(!CONFIGR)				//User asking for commissiioning comm parameters
		{
		init_comm();			//Write set up comm to EEPROM parameters
		get_su();				//Update parameters
		}
	switch(State)
		{
		case Idle:		measure();
			break;
		case Vett:		vett();
			break;
		case Process:	process();
			break;
		case Reply:		reply();
			break;
		}
	}
}
//			End of main()


//enum	{Q_rate, E_rate, Temp_loc, Temp_rem, Q_tot, E_tot, Delta_t};

/*	This is the idle function which executes until there is a comm interrupt. It will
	accumulate Huba interrupts and count real time for about 2 seconds then calculate 
	Huba freq and hence flow rate. At the end of 2 seconds, temperature is measured.
	Energy is calculated and added total. Every 10 minutes, the accumulated energy and
	flow is updated to EEPROM to be recalled later, or after a power cycle. ten minute 
	writes are to stay within the EEPROM write endurance for 10 years or more
*/
void measure(void)
{
double	q_time, scratch;	//Precise time for number of Q_ints
double	q_rate, e_rate;	//Flow and Energy in g/m and BTU/m
double	m_rate;				//Lbs/min
double	density;				//medium density at local temperature 
double	unit_energy;		//When => 1, give a pulse out		
	
Meas.done  = Meas.rtd = Meas.loflo = 0x00;
TMR4IE = TMR4IF = 0;			//Keep Tmr4 off
TMR4 = 0;						//TMR4 detects zero flow
Q_time = Q_ints = 0;			//Reset flow and time accumualtors
TMR6IE =	ON;					//Start flow timer in case flow = 0
//Get stored energy and flow in selected units from totalizer EEPROM
//Stored_q_tot = read_eeprom_double(TOTAL_BASE_ADD + F_TOTAL_ADD);
//Stored_e_tot = read_eeprom_double(TOTAL_BASE_ADD + E_TOTAL_ADD);
while(RCIF)
	Dummy = RCREG;				//Clear out any stray interrupts
INTF = 0;						//Reset INTF flag
INTE = ON;						//Allow Huba interupts to start counting
CREN = OFF;
CREN = ON;						//Clear any OERR or FERR errors
//Comm.frame = Comm.fc_err =  Comm.err = Comm.for_us = Comm.rx = 0;//Zero all comm flags
RCIE = ON;						//Now start listening
//Now wait for measurement of flow to finish or a Comm interupt
while(!Meas.done && !Comm.rx)			//Wait till measure is done or a comm int
	{											//While waiting and receiving messages not for us
	if(Comm.frame && (TMR0 > 250))	// set to receive again after line is idle for 8 ms
		Comm.frame = 0;
	}
if(Comm.rx)						//We have a message coming
	{
	while((Buf_ptr - Comm_buf) < 8 && (TMR0 < 250));//Cheat. We can do this because only
			//FC 03,04,05, 06 are valid and all are 8 bytes long. Don't hang if never get 8 bytes

/* In anticipation of Clark flow meters needing calibration
	if(Comm_buf[1] == 0x10)	//We are in factory mode and writing Dz or K
		while((Buf_ptr - Comm_buf) < 14 && (TMR0 < 250));
*/
	if(Comm.for_us)						
		Length = Buf_ptr- Comm_buf;
	else
		{
		Comm.frame = Comm.fc_err =  Comm.err = Comm.for_us = Comm.rx = 0;//Zero all comm flags
		while(TMR0 < 250);	//Wait until line is idle
		}
	State = Vett;				//Determine if good message for us.
	}
else if(Meas.done)
	{	//enum	{Q_rate, E_rate, Temp_loc, Temp_rem, Q_tot, E_tot, Delta_t};
	q_time = (Q_time + TMR6/256)*.008192;	//Precise time,secs, for Q_ints
	if(Q_ints > MIN_INTS)				//Frequency will not be zero
		{
		FreqH = (Q_ints -1)/q_time;	//No of Huba interrpts in measured time
		density = calc_temps();			//Get and store temperatures, return H2O density
		scratch = Read_regs[Temp_rem] - Read_regs[Temp_loc];
		Read_regs[Delta_t] = scratch;	//Delta temp
		q_rate = pulse_out_type();		//This is the rate in gal/min from the Huba
			// The .133681*density converts volumetric flow to mass flow and to BTUs
		mass_rate = q_rate*.133681*density;	//Lbs/min
		e_rate = mass_rate*fabs(Read_regs[Temp_rem] - Read_regs[Temp_loc]);
		}
	else 			//If there is no f\measureable flow, then flow and energy this period = zero
		{
		FreqOut = 0;
		q_rate = e_rate = 0.0;
		}
	set_Fout(FreqOut);				//Set the output pulse rate as determined in pulse_out_type
	//Now convert gal/min and BTU/min to chosen units and put to holding registers.
	Read_regs[Q_rate] = q_rate*ConvQ;	//Put flow and energy away in selected units
	Read_regs[E_rate] = e_rate*ConvE;
	Read_regs[M_rate] = m_rate*ConvM;
//Now convert to chosen storage units and add in stored units
	Read_regs[Q_tot] += ConvQS*(Rt_ints*TIME_BASE*q_rate);	// Add to current totals
	Read_regs[E_tot] += ConvES*(Rt_ints*TIME_BASE*e_rate);
	Read_regs[M_tot] += ConvMS*(Rt_ints*Time_BASE*m_rate	
	Rt_ints = 0;					//Start new timing period
// Tmr1 interrupts every .262 seconds, and there are Rt_int number of interrupts
	N_meas++;
	if(N_meas > 30)				//10 minutes worth of measurements
		{
		write_eeprom_double(TOTAL_BASE_ADD + F_TOTAL_ADD, scratch);	//Store new total flow
		write_eeprom_double(TOTAL_BASE_ADD + E_TOTAL_ADD, scratch);	//Store new total energy
		N_meas  =0;						//Reset for next 10 mins
		}
	State = Idle;
	}
}					//End of measure()

/* Depending on which Huba meter is used, whether flow or energy is on pulse
	output, and what flow or energy units are used, the flow rate is returned
	 and output pulse frequency determined
*/
double	pulse_out_type(void)
	{
	double	q_rate;
	if(Config.freq_type == 0)			//Requested Flow rate on pulse output
		{
		Pulse_width = FLOW_PW;			//Set pulse width to 2 ms for flow
		#ifdef _H34
			q_rate = (.373*FreqH -.3)/3.785412;		//Flow in gal/min
			if(Config.q == 1)				//Flow units are l/m
				FreqOut = 9.46353*q_rate;//Flow in l/m, Flow = .4*FreqOut
			else if(Config.q == 2)		//Flow units are l/sec
				FreqOut = 10.515*q_rate;//Flow in l/s, Flow = .006*FreqOut
			else
				FreqOut = 10*q_rate;		//Flow in gal/min, Flow = .1*FreqOut
		#endif
		#ifdef _H12
			q_rate = (.187*FreqH -.2)/3.785412;		//Flow in gal/min
			if(Config.q == 1)				//Flow units are l/m
				FreqOut = 18.927*q_rate;//Flow = .2*FreqOut
			else if(Config.q = 2)		//Flow units are l/sec
				FreqOut = 18.02577*q_rate;//Flow in l/s, Flow = .0035*FreqOut
			else
				FreqOut = 16.6667*q_rate;	//Flow in gal/min, Flow = .06*FreqOut
		#endif
		}
	else											//Energy on Pulse output
		{
		Pulse_width = ENERGY_PW;			//Set pulse width to 5 ms for energy



		}	
	return(q_rate);
	}


// Come here to decide what to do with message.
void vett(void)	
	{
	uint16 crc, mCrc;

	if(Comm.for_us && !Comm.err)		//For us and no comm err
		{
		if(Comm_buf[0] == My_add)		//Not the broadcast addresss
			{
			crc = CRC16(Comm_buf, Length-2);	//Calculate CRC of message
			mCrc = ((Comm_buf[Length-2] << 8) | Comm_buf[Length - 1]); 
			if(!(mCrc^crc)&& !Comm.err)		//CRCs match and no comm error
				State = Process;					//See what to do
			else
				State = Idle;
			}
		}
	else
		State = Idle;
	}
						//No reply if error}
/* This function writes data to the designated register 
*/
void	write_word(byte fc)
	{
	uint16	start_reg, base, offset;//Beginning logical register
	int16		local_reg;					//Physical reg no.
	byte		add_err = NO;				//Register is out of allowed range
	byte		d_err;						//Data range error
	byte		ep_add;						//EEPROM address for data.(if Pic16F1939, need int)
	uint16	crc, tempcrc;				//CRC value
	static	byte	*r_ptr;				//Traversing pointer
	byte		length;			//Buffer length for CRC calc	

	r_ptr = Reply_buf;					//Set up tp fill Reply buffer
	*r_ptr++ = My_add;					//Begin with our ID
	start_reg = ((Comm_buf[2] << 8) | Comm_buf[3]);	//Register to write
	base = BASE_WRITE_REGS;				//Assume writing configuration registers
	offset = OP_BASE;
	if((!Config.config) && (start_reg >= BASE_COMM_REGS))	//Writing commisioning registers
		{
		base = BASE_COMM_REGS;
		offset = COMM_BASE;
		}
	if(fc == 06) 							//Write registers
		{
		local_reg = start_reg - base;
		ep_add = 2*local_reg + offset;	//Actual EEPROM address
		if((local_reg  < 0) || (local_reg >  MAX_WRITE_REGS ))
			add_err = YES;
		}
	else if(fc == 16)
		{
		local_reg = start_reg-BASE_FAC_REGS;	//K and Dz values are not offset
		ep_add = 4*local_reg ;						//Actual EEPROM address
		if((local_reg  < 0) || (local_reg > MAX_FAC_REGS))	//Only two registers are used
			add_err = YES;
		}
	if(fc == 5) 						//Coil actions
		{
		local_reg = start_reg - BASE_COIL_REGS;
		if((local_reg  < 0) || (local_reg >  MAX_COIL_REGS ))
			add_err = YES;
		d_err = YES;
		if((Comm_buf[4] == 0x00) || (Comm_buf[4] == 0xFF))
			d_err = NO;			// Modbus says other values are not valid		
		if((d_err == NO) && (add_err == NO))
			{
			switch(local_reg)
				{
				case 0:	write_eeprom_double(TOTAL_BASE +F_TOTAL_ADD, 0.0);//Reset Flow total
							Read_regs[Q_tot] = 0.0;
					break;
				case 1:	write_eeprom_double(TOTAL_BASE +E_TOTAL_ADD, 0.0);//Reset Energy total
							Read_regs[E_tot] = 0.0;
					break;
				case 2:	
							eeprom_write(COIL_BASE + M_TOTAL_ADD, 0.0); 		//Reset Mass total
					break;
				case 3:		init_defaults();//Reset all units to factory defaults except comm parameters
					break;
				default:
						;			//Do nothing
				}
			}
		}
	if(add_err == YES)				//Bad register address
		{					//Bad addressing
		*r_ptr++ = fc | 0x80;		//Bad adress space
		*r_ptr++ = BAD_DATA_ADD;	//Set Exception code 02
		}
	if(d_err == YES)					//Bad register address
		{					//Bad data
		*r_ptr++ = fc | 0x80;		//Bad adress space
		*r_ptr++ = BAD_DATA_RANGE;	//Set Exception code 03
		}
	else										//Legal data
		{
		*r_ptr++ = fc;						//Put in fc, reg no, and reg value
		*r_ptr++ = Comm_buf[2]; 	*r_ptr++ = Comm_buf[3];	//Put in reg no.
		*r_ptr++ = Comm_buf[4]; 	*r_ptr++ = Comm_buf[5];	//Put in reg value
		if(fc == 06)						//Now put data away
			{
			write_eeprom_int(ep_add,Comm_buf[4], Comm_buf[5]);
			crc = read_eeprom_int(ep_add);
			Dummy = crc;
			}
		else if(fc == 16)					//Writing ints to a double
			{
			write_eeprom_int(ep_add,Comm_buf[7], Comm_buf[8]);
			write_eeprom_int(ep_add+2,Comm_buf[9], Comm_buf[10]);
			}
		init_comm();						//Update any new parameters  			
		}
	//Now reply
	length = r_ptr - Reply_buf;				//Calculate and add in CRC
	tempcrc = crc = CRC16(Reply_buf, length);
	*r_ptr++ = tempcrc>> 8;						//Put CRC in
	*r_ptr   = (byte)crc;
	Length = length+2;							//Set for transmitting
	State = Reply;									//Go yee forth and reply
	get_su();				//Update parameters
	}

//Come here if request to read holding registers that are doubles
//Could read up tp 6 doubles or 24 bytes + overhead
//Handles exception codes 01 and 02
void	build_read_resp(byte fc)		//Valid FC is 03 or 04
	{
	uint16	start_reg, base_reg;		//Beginning register
	uint16	reg_count, max_read_regs;	//No of regs to read	
	uint16	crc, tempcrc;				//CRC value
	byte		*r_ptr;			//Traversing pointers
	double	*arry_ptr;
	byte		length;						//Buffer length for CRC calc
	byte		config;	

	r_ptr = Reply_buf;					//Set up tp fill Reply buffer
	*r_ptr++ = My_add;					//Begin with our ID	
	start_reg = ((Comm_buf[2] << 8) | Comm_buf[3]);	//Start register
	reg_count = ((Comm_buf[4] << 8) | Comm_buf[5]);	//No of registers
//	reg_count /= 2;
	config = (CONFIGD && CONFIGR) ? 0 :1;
if((fc == 03) && config)	//Not reading Dz or K
		{
		base_reg = BASE_READ_REGS;
		max_read_regs = MAX_READ_REGS;
		}
	else if(( fc== 03) && !config)				
		{
		base_reg = BASE_FAC_REGS;
		max_read_regs = MAX_FAC_REGS;
		}
	if(Comm.fc_err)					//Invalid Function Code
		{
		*r_ptr++ = fc | 0x80;		//Bad address space
		*r_ptr++ = BAD_FC;			//Set Exception code 02	
		}
	else if(start_reg < base_reg || ((start_reg - base_reg + reg_count) > max_read_regs))
		{					//Bad addressing
		*r_ptr++ = fc | 0x80;		//Bad adress space
		*r_ptr++ = BAD_DATA_ADD;	//Set Exception code 02
		}		
	else									//Legal data
		{
		*r_ptr++ = fc;					//Put in fc
		*r_ptr++ = 2*reg_count;		//4 bytes per double
		arry_ptr = Read_regs +(start_reg/2- BASE_READ_REGS);	 //First requested reg
		while(reg_count)			//Load all requested registers
			{
			read_double(arry_ptr,r_ptr);
			r_ptr+= 4;
			arry_ptr++;
			reg_count -= 2;
			}

		}
	length = r_ptr -Reply_buf;					//Calculate and add in CRC
	tempcrc = crc = CRC16(Reply_buf, length);
	*r_ptr++ = tempcrc>> 8;						//Put CRC in
	*r_ptr   = (byte)crc;
	Length = length+2;							//Set for transmitting
	State = Reply;									//Go yee forth and reply
	}


//Come here to compose reply to client. Made up response to read TempLoc
void reply(void)
	{
	TXENB = YES;						//Enable Transceiver	
	RCIE = OFF;			//TXENB = YES
	Buf_ptr = Reply_buf;
	Comm.tx = ON;						//Say we are transmitting
	TXIE = ON;							//Enable Tx interrupts
	while(Comm.tx == ON);
	TXENB = OFF;
	CREN = 0;							//Clear OERR errors
	CREN = 1;
	RCIE = ON;							//Get next message
	State = Idle;						//Done with response
	do
		Dummy = RCREG;
	while(RCIF);
Comm.frame = Comm.fc_err =  Comm.err = Comm.for_us = Comm.rx = 0;//Zero all comm flags
	}			//End of reply()


/*	This routine averages 16 readings of hi and lo calibration resistors
	to determine Sigma and Rho parameters needed to calculate temperatures
*/
void cal_rtd(void)		
{
uint16 	cnts = 0;
byte		ind;

for(ind = 0; ind <32; ind ++)	//Get hi cal resistor reafdings
	cnts += get_rtd(0x08);
cnts/= 32;
Counts[3] = cnts;					//Store average hi cal reading
cnts = 0;
for(ind = 0; ind <32; ind ++)	//Get lo cal resistor counts
	cnts += get_rtd(0x10);
cnts /= 32;
Counts[4] = cnts;
Sigma = (Counts[3] - Counts[4])*CONSTR -(Counts[3] + Counts[4])/2;
Sigma /= 1024;						//Make ratiiometric
Rho = (Counts[3] - Counts[4])*CONSTK;			//See pg 24, NB #5
Rho /= 1024;
}

double	calc_temps(void)
{
double	cntdouble;
double	scratch,rtrn;
double	rtd, rtdr;						//Resitance values
uint16 	cnts = 0;
byte		ind;
		
for(ind = 0; ind <32; ind ++)	//Get remote rtd, single rtrn
	cnts += get_rtd(0x01);
cnts/= 32;
Counts[0] = cnts;					//Store average single remote
cnts = 0;
for(ind = 0; ind <32; ind ++)	//Get remote rtd, double rtrn
	cnts += get_rtd(0x03);
cnts/= 32;
Counts[1] = cnts;					//Store average double remote
cnts = 0;
for(ind = 0; ind <32; ind ++)	//Get local rtd
	cnts += get_rtd(0x04);
cnts/= 32;
Counts[2] = cnts;					//Store local rtd
cntdouble = Counts[2];			//Calculate local rtd resistance
cntdouble /=1024;
rtd = ((cntdouble +Sigma)*RA/(Rho -cntdouble - Sigma));
scratch = rtd-1000;
scratch = (rtd -1000)/3.85;	//Local in Degs C
scratch = 9*scratch/5 + 32;	//Convert to Deg F
rtrn =  Cal_rho[0]*scratch*scratch + Cal_rho[1]* scratch + Cal_rho[2]; //Calculate density
Read_regs[Temp_loc] = scratch;//Put into modbus reg
cntdouble = Counts[0];			//Calculate rtd resistance, single remote			
cntdouble /=1024;
rtd = ((cntdouble +Sigma)*RA/(Rho -cntdouble - Sigma));
cntdouble = Counts[1];			//Calculate rtd resistance, double remote
cntdouble /=1024;
rtdr = ((cntdouble +Sigma)*RA/(Rho -cntdouble - Sigma));	//Remote, double return
scratch = ((4*rtdr-3*rtd)- 1000)/3.85;	//Remote temperature
scratch = 9*scratch/5 + 32;				//Convert to Deg F
Read_regs[Temp_rem] = scratch;			//Put into modbus reg
TMR0 = 0;
return(rtrn);		
 }

//Gets A/D counts for the RTD being measured.
			
uint16	get_rtd(byte loc)
	{
	uint16	rtrn;
	
	PORTC = loc;					//Select rtd to be read
	TMR0 = 0;
	while(TMR0 <200);				//FET settle time
	ADGO = ON;						//Start conversion
	while(ADGO);					//Wait
	rtrn = ADRESH << 8;			// NRZ on Fet selection
	rtrn	|= ADRESL;
	return(rtrn);	//Ratiometric values to 10 bit A/D
	}

// We have a potentially valid message. It is for us and free of error
void		process(void)
	{
	switch(Comm_buf[1])						//Check function code
		{
		case	03:		build_read_resp(Comm_buf[1]);	// Get requested data for reply
							break;
		case	05:			write_word(5);		//Update holding registers
							break;
		case	06:			write_word(6);		//Update holding registers
							break;
		case	16:			write_word(16);	//Update Dz or K
							break;
		default:			Comm.fc_err = YES;	//Invalid function code
							build_read_resp(Comm_buf[1]);
		}
	}

//	Calculate a CRC word and swaps resultant bytes

uint16 CRC16 (byte *nData, uint16 wLength)
{
	byte nTemp;
	uint16 wCRCWord = 0xFFFF;
	uint16 bswap;
	
	while (wLength--)
		{
	   nTemp = *nData++ ^ wCRCWord;
	   wCRCWord >>= 8;
	   wCRCWord  ^= wCRCTable[nTemp];
		}
	bswap = wCRCWord >>8;
	wCRCWord << = 8;		
   return(wCRCWord | bswap);
}
 // End: CRC16



/*	Interupt Service Routine isr()
Always enabled, services all timers and comunication interrupts.
*/
void interrupt isr(void)       
{
 if(RCIF && RCIE)
   {
	if(Comm.frame == 0)						//First char after T3.5
		{
		Buf_ptr = Comm_buf;					//To traverse Comm_buf
		Comm.nine = RX9D;						//Read Parity bit
		Rx_char =	RCREG;
		*Buf_ptr++ = Rx_char;				//Read all chars, advance ptr
		Comm.frame = YES;						//Start of frame
		if(((Comm_buf[0] == My_add) ||(Comm_buf[0] == 0x00)) && !(OERR || FERR))
			{
			Comm.for_us = YES;				//Might have to reply
			Comm.rx = YES;							//Let others know
			}
		else
			{
			Comm.for_us = NO;					//Not our address
			Comm.rx = NO;
			}
		}
	else 											//Next byte
		{
		if(Comm.for_us)
			{
			Comm.nine = RX9D;					//Read ninth bit
			Rx_char =	RCREG;
			*Buf_ptr++ = Rx_char;			//Fill buffer if for us
			if(!RX && (TMR0 > 7))			//Failed intra char delay
				Comm.err = YES;
			}
		else										//Not for us, but need to check end of Tx
			Dummy = RCREG;						//Need to empty RCREG to get next int
		}
		if(Comm.for_us && !Comm.err)		//Calculate parity
			{
			Parity = 0;							//Do parity check
			while(Rx_char != 0) 
				{ 
				Parity++; 
				Rx_char &= (Rx_char-1); 	//The loop will execute once for each bit of ino set 
				}
			Parity &=0x01;						//Parity will be 1 if Even Parity
			Parity ^= Comm.nine;				//Zero if master uses Even, 1 if master uses Odd
			if(((Sel_parity == EVEN) && Parity) || ((Sel_parity == ODD) && !Parity))
				Comm.err = YES;				//This byte failed parity
			if(OERR||FERR)
				{			
				SPEN = OFF;							// char time > 1.5 char time
				SPEN = ON;							// If buffer is overrun or inter
				Comm.err = YES;
				}
			}
	TMR0 = 0;
	}

	if(TXIF && TXIE)
	   {	
	  if(Length--)							//Send until end of message
			{
	   	Rx_char = *Buf_ptr;			//Send a byte and point to next
			Parity = 0;						//Do parity check
			while(Rx_char != 0) 
				{ 
				Parity++; 
				Rx_char &= (Rx_char-1); //The loop will execute once for each bit of in the buffer
				}
			Parity &=0x01;					//Parity will be 1 if Even Parity
			if((Sel_parity == EVEN) && (Parity == 0)) 
				TX9D = 0;					
			else if((Sel_parity == ODD) && (Parity == 0) || (Sel_parity == 0)) 
				TX9D = 0x01;//Write 9th bit first,If no parity, this is second stop bit
			else
				TX9D = 0;
			TXREG = *Buf_ptr++;			//Send a byte and point to next
			Dummy = Length;
			while(TRMT);
			}
	   else
	      {
	      while (!TRMT);				//Wait for TSR to empty
	      Comm.tx = OFF;				//Say we are done
	      TXIE = OFF;
      	}
   	}
	if(TMR2IE && TMR2IF)				//Timer 2 interrupts every .128 ms
  	{
	Tmr2_ticks--;						//Decides on pulse width
	if(Tmr2_ticks == 0)
		PULSE = OFF;					//Turn Pulse output off;
	 if((Nl==0) && (Ns ==0))		//After countdown, turn pulse out on
	 	{
	 	Nl = NTau1;						//and start new countdown
	 	Ns = NTau2;
	 	PULSE =  ON;					//Pulse output is enabled low
		Tmr2_ticks = Pulse_width;	//No of ints for pulse width
	 	}
	  if(Nl >0)
	  	{
	  	Nl--;								//Count down NTau1
	  	TMR2 = T0_OFFSET;
	  	}
	  else 
	  	{
	  	TMR2 = Ns + T0_OFFSET;		//After Ntau1 ==0, count down Ntau2
	  	Ns = 0;
	  	}
	  TMR2IF = OFF;
	} 
	if(TMR6IE && TMR6IF)
	{
		Q_time++;					//Count TMR6 ints each 8.192 ms
		if(Q_time > 233)			//2 seconds is up. Measured 7/27
			Meas.done = YES;		//Clock still runs
		TMR6IF = OFF;
	}									//Set to stop clock		
			
//Counts Huba flow pulses		 						
	if(INTE && INTF)				//Interrupts on HUBA flow
  	{
	if(Q_ints == 0)	
		{
		Q_time = 0;					//Start counting on first HUBA pulse
		TMR6IF = OFF;				//First int, start TMR6
 	 	TMR6 = 0x00;				//Begin counting 2 sec time
 		} 					
   Q_ints++;						//Tally Huba ints
   if(Meas.done)					//Here if first int after 2 secs								
   	{
	   TMR6IE = OFF;
	   INTE = OFF;					//No more q counts
		TMR4IE = OFF;				//No false no-flow
	   }
  	INTF = OFF;
  	TMR4	= 0x00;					//Reset to
 	}
   if(TMR4IE && TMR4IF)
  	{
	   Meas.loflo = YES;				//Huba freq < 10
	   Meas.done = YES;				//Stop 
	   TMR4IE = OFF;					//No more need
	   TMR4IF = OFF;
   }
	if(TMR1IF && TMR1IE)			//Timer 1 int every .262144 secs
	   {
	   Rt_ints++;					//Count interrupts
	   TMR1IF   =   OFF;			//Reset IF flag
	   }

}
//					End of isr()

/*	Initialization.  Sets up all registers. TMR1ON and IF are not
   initialized so interrupts do not happen until invoked by the
*/

//Initialize the PIC16F1936
void	init_1936(void)
{
ANSELB	= ANSELB_INIT;
ANSELA	= ANSELA_INIT;
TRISC 	= TRISC_ALL;
TRISB 	= TRISB_ALL;
OSCCON 	= OSCCON_INIT;
TRISA 	= TRISA_ALL;
PORTB		= PORTB_INIT;
WPUB		= WPUB_INIT;
TMR0IE	= OFF;				//No Timer 0 interrupts
TMR2IE 	= OFF;
TMR4IE	= OFF;
TMR6IE	= OFF;
T1CON   	= T1CON_INIT;
T2CON		= T2CON_INIT;
T1GCON 	= 0x00;
TMR1IE	= ON;					
//T2CON		= T2CON_INIT;		//No TMR1 gate functions
T6CON		= T6CON_INIT;
PR2		= 0xFF;				//Full TMR2 period
PR6		= 0xFF;				//Full TMR6 period
OPTION_REG	= OPTION_INIT;
INTCON  	= INTCON_INIT;
CCP1CON	= CCP1CON_DATA;	//No PWM function, PORTC <2> is affected.
RCIE		= OFF;
TXENB		= OFF;
TXEN		= ON;
ADCON0	= ADCON0_INIT;			//Selects Cahn 0
ADCON1	= ADCON1_INIT;			//Selects Reference, format, Tad
SYNC		= 0;						//For all Baud rates at Fosc = 8 Mhz
BRG16		= 1;					
BRGH		= 1;					
RCSTA		= RCSTA_INIT;
RX9		= ON;						//All communication is at 9 bits
TX9		= ON;
RXENB		= NO;						//Enable receiver


//   All other register power up with 0X00 which disables all functions
}
//					End of init_1936()

void		init_comm()		//Set up commissioning parameters
	{
	write_eeprom_int(COMM_BASE + ID_ADD,  0x00, SETUP_ADD;	//Set commissioning address
	write_eeprom_int(COMM_BASE + BR_ADD,  0x00, SETUP_BR;		//Set commissioning address
	write_eeprom_int(COMM_BASE + PARITY_ADD, 0x00, SETUP_PARITY;	//Set commissioning address
	}

void	init_defaults(void)		/Sets all set units to factory defaults
{
		//Store defaults to EEPROM
	write_eeprom_int(OP_BASE + Q_UNITS_ADD,  0x00, G_MIN);	//Set flow rate units to g/m
	write_eeprom_int(OP_BASE + E_UNITS_ADD,  0x00, BTU_MIN);	//Set energy rate units to btu/m
	write_eeprom_int(OP_BASE + M_UNITS_ADD,  0x00, LBS_MIN);	//Set mass rate units to lbs/m
	write_eeprom_int(OP_BASE + QS_UNITS_ADD, 0x00, GS);		//Set flow total units to gals
	write_eeprom_int(OP_BASE + ES_UNITS_ADD, 0x00, KBTU);		//Set energy total units to kBTU
	write_eeprom_int(OP_BASE + MS_UNITS_ADD, 0x00, LB);		//Set mass total units to lbs
	write_eeprom_int(COIL_BASE + SELECTP_ADD,0x00, 0X01);		//Set pulse output to energy
	write_eeprom_int(COIL_BASE + SELECTT_ADD,0x00, 0X00);		//Set temp units to F

}
void	get_su(void)
{
byte	value;

		//Assign baud rate
		value = eeprom_read(COMM_BASE + BR_ADD+1);
		switch (value)
			{
			case 1:	//9600 baud request	
							SPBRGH = 0;
							SPBRGL = SPBRGL96;
			break;
			case 2:		//19.2K baud request	
							SPBRGH = 0;
							SPBRGL = SPBRGL19;
			break;
			default:
							SPBRGH = 0;
							SPBRGL = SPBRGL96;
			}

	Sel_parity 		= 		eeprom_read(COMM_BASE + PARITY_ADD+1);	//Assign Parity
	My_add = 				eeprom_read(COMM_BASE + ID_ADD+1);		//Assign ID
	Config.freq_type = 	eeprom_read(COIL_BASE +SELECTP_ADD+1;
	Config.q			= 		eeprom_read(OP_BASE +Q_UNITS_ADD+1);	//Set Flow rate units 
	Config.e			= 		eeprom_read(OP_BASE +E_UNITS_ADD+1);	//Set Energy rate units. 
	Config.m			= 		eeprom_read(OP_BASE +M_UNITS_ADD+1);	//Set Mass rate units.
	Config.qs		= 		eeprom_read(OP_BASE +QS_UNITS_ADD+1);	//Set Energy store units 
	Config.es		=		eeprom_read(OP_BASE +ES_UNITS_ADD+1);	//Set Energy store units 
	Config.ms		=		eeprom_read(OP_BASE +MS_UNITS_ADD+1);	//SetMass store units
	Config.config 	= CONFIG_DONE;		//Record commissioning configuration.
	ConvQ = 	Conv[Config.q];			//Get selected conversion constants
	ConvE = 	Conv[Config.e];
	ConvM =  Conv[Config.m];
	ConvQS =	Conv[Config.qs];
	ConvES = Conv[Config.es];
	ConvMS=  Conv[Config.ms];
	}



/* The compiler stores doubles little endian, but mod bus wants big endian
	Therefore read last byte of double into first byte of Reply_buf
*/
void	read_double(double *src, byte *dest)
	{
	byte i;
	byte *ptr;
	
	ptr = (byte*)src +3 ;	//Point to last byte of the double
	for(i= 0;i <4; i++)
		{
		*dest = *ptr;			//Load double to Reply buffer
		dest++;
		ptr--;
		}
	}


// Reads a double from the passed address
double	read_eeprom_double(byte d_add)
	{
	byte	i;
	byte *ptr;	
	double rtrn;
	
	ptr = (byte*)&rtrn;
	for(i= 0; i<4; i++) 
		{
		*ptr = eeprom_read(d_add);
		ptr++;
		d_add++;
		}
	return(rtrn);
	}
// Writes a double to the passed address
void	write_eeprom_double(byte d_add, double d_data)	
	{
	byte i;
	byte *ptr = (byte *) (&d_data);

	for(i = 0; i<4; i++)
		{
			EEIF = OFF;
			eeprom_write(d_add, *ptr);
			ptr++;
			d_add++;
			asm("clrwdt");
			while(!EEIF);
		}
	}

void		write_eeprom_int(byte d_add, byte hi, byte lo)	//Write uint16 data to EEPROM	
	{
Dummy = d_add;
	EEIF = OFF;			
	eeprom_write(d_add, hi);			//Write MSB
	d_add++;
Dummy = d_add;
	while(!EEIF);							//Wait for write to complete
	eeprom_write(d_add,lo);			//Write LSB
	while(!EEIF);							//Wait for write to complete
	}

uint16	read_eeprom_int(byte add)
	{
	uint16	rtrn;
	rtrn  = eeprom_read(add++);	//Hi byte
	rtrn = (rtrn << 8) | eeprom_read(add);
	return(rtrn);
	}
//Puts A/D counts away to Count[5] for subsequent temp calculations


//Set output pulse frequency.
void	set_Fout(double freq)	
{
	double 	tau,ntau;
	double	ival,fval;

	freq = (freq > 525) ?525 : freq;
	if(freq <10)							//If less than turn down, set pulse hi
		{
		TMR2IE = OFF;							// and turn off T0 interrupts					
		PULSE = DISABLED;
		}
	else
		{
		TMR2IE = ON;
		tau = 1/(2*freq);						//1/2 period of output Freq
		ntau	= tau*CLK_FREQ*1e6/1024;	//Number of TMR2 interrupts
		fval = modf(ntau, &ival);			//Fractional interrupt		
		NTau1 = (uint16)ival ;				//Integral # of ints
		NTau2 = (uint16)(255*(1-fval));	//Final T0 interrupt time
		Nl = NTau1;
		Ns = NTau2 + T0_OFFSET;				//Tweak last interrupt
		Ns = (Ns > 253) ? 0 : Ns;
		}
}

   
/*
Read_regs[0] = 10.1;					//Dummy variables,flow, energy, etc
Read_regs[1] = 20.2;					//For debug only
Read_regs[2] = 30.3;
Read_regs[3] = 40.4;
Read_regs[4] = 50.5;
Read_regs[5] = 60.6;
*/
