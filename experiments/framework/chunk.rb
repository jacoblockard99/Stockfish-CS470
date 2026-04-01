def chunk(chunksize, lines, msgs)
    i = 0
    while i < lines.size
        print "Continue with #{i}-#{i+chunksize}? [Y/n] "
        exit 1 if $stdin.gets.chomp == "n"
        j = 0
        while i+j < lines.size && j < chunksize
            `#{lines[i+j]}`
            puts msgs[i+j]
            j += 1
        end
        i += j
    end
end