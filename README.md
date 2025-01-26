This project is disigned for interactive laboratory of electronics in university. 
Concept of this app is to exchange data with STM32 via UART.

General structure:
- main.py  -  inherits classes from other files, draws UI, sets UI interaction
- port_interaction.py  -  file with class SerialPort which is responsible for converting, reading and sending data to UART
- randomer.py (I agree, bad name)  -  contains class Data which implements data storage and interaction by pandas library.
  Also implements dinamic visualization of Data if needed.
- interface.ui  -  file with interface and some window setup (gets loaded in main.py during initialisation)
