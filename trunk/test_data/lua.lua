-- Lua Syntax Test File
-- Some comments about this file

print "Hello World"
print "An Open String

function factorial(n)
  if n == 0 then
    return 1
  end
  return n * factorial(n - 1)
end

fibs = { 1, 1 }
setmetatable(fibs, {
  __index = function(name, n)
    name[n] = name[n - 1] + name[n - 2] 
    return name[n]
  end
})