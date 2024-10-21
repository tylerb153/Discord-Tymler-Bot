def main():
    while True:
        message = input("Enter message: ")
        messages = message.split(" ")
        userString = ""
        for word in messages:
            def removeY(word) -> str:    
                if word.endswith('y'):
                    word = word[:-1] + 'ie'
                if word.endswith('Y'):
                    word = word[:-1] + 'IE'
                return word
            def removePunctuationThenConvert(word: str) -> str:
                punctuation = '*~`!@#$%^&()_+={}[]|\\;\'"<>,?/.-'
                if word[-1] in punctuation:
                    return removePunctuationThenConvert(word[:-1]) + word[-1]
                else:
                    return removeY(word)
            word = removePunctuationThenConvert(word)
                
            userString += word + " "
        print(userString)
            
        


        

if __name__ == '__main__':
    main()