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
        Task1c.task1c(arguments[2],arguments[3])
    elif arguments[1]=='task1d':
        Task1d.task1d(arguments[2],arguments[3])
    else:
        print 'enter valid inputs'

	
