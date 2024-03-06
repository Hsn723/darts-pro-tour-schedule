from tour import Tour

def main():
    [tour().output_calendar() for tour in Tour.__subclasses__()]

if __name__ == '__main__':
    main()
