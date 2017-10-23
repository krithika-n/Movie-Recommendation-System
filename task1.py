import task1_a_b
import Task1c
import Task1d
import sys
if __name__ == '__main__':
    arguments=sys.argv
    if arguments[1]=='task1a':
        task1_a_b.task1_a(arguments[2],arguments[3])
    elif arguments[1]=='task1b':
        task1_a_b.task1_b(arguments[2],arguments[3])
    elif arguments[1]=='task1c':
	if int(arguments[3]) == 1:
	        Task1c.task1c(int(arguments[2]),int(arguments[3]),0)
	else:
		Task1c.task1c(int(arguments[2]),int(arguments[3]),int(arguments[4]))
    elif arguments[1]=='task1d':
	if int(arguments[3]) == 1:
	        Task1d.task1d(int(arguments[2]),int(arguments[3]),0)
	else:
		Task1d.task1d(int(arguments[2]),int(arguments[3]),int(arguments[4]))
    else:
        print 'enter valid inputs'

	
