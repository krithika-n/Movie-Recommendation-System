import tasks
import sys

if __name__ == '__main__':
    arguments=sys.argv
    if arguments[1]=='load_tables':
        try:
            tasks.loadAllTables()
        except Exception as e:
            print e
    elif arguments[1]=='print_actor_vector':
        try:
            tasks.print_actor_vector(int(arguments[2]), int(arguments[3]))
        except Exception as e:
            print e
    elif arguments[1]=='print_genre_vector':
        try:
            tasks.print_genre_vector(arguments[2],int(arguments[3]))
        except Exception as e:
            print e
    elif arguments[1]=='print_user_vector':
        try:
            tasks.print_user_vector(int(arguments[2]), int(arguments[3]))
        except Exception as e:
            print e
    elif arguments[1]=='differentiate_genre':
        try:
            tasks.differentiate_genre(arguments[2],arguments[3], int(arguments[4]))
        except Exception as e:
            print e
    else:
        print 'invalid arguments passed'