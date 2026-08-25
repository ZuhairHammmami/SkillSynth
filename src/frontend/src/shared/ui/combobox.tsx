"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Search, Check, ChevronDown } from "lucide-react"
import { cn } from "@/shared/lib/utils"

interface ComboboxOption {
  value: string
  label: string
  subtitle?: string
}

interface ComboboxProps {
  options: ComboboxOption[]
  value?: string
  onSelect: (value: string) => void
  placeholder?: string
  emptyText?: string
  className?: string
  disabled?: boolean
}

export function Combobox({
  options, value, onSelect, placeholder,
  emptyText, className, disabled,
}: ComboboxProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const filtered = options.filter(
    (o) => o.label.toLowerCase().includes(query.toLowerCase())
      || o.subtitle?.toLowerCase().includes(query.toLowerCase())
  )

  const selected = options.find((o) => o.value === value)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleSelect = useCallback((optValue: string) => {
    onSelect(optValue)
    setOpen(false)
    setQuery("")
  }, [onSelect])

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      <div
        className={cn(
          "flex h-9 w-full items-center gap-2 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors",
          "focus-within:outline-none focus-within:ring-1 focus-within:ring-ring",
          disabled && "cursor-not-allowed opacity-50",
        )}
      >
        <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
        <input
          ref={inputRef}
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls="combobox-list"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true) }}
          onFocus={() => setOpen(true)}
          placeholder={selected ? selected.label : placeholder}
          disabled={disabled}
          className="flex-1 bg-transparent outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed"
        />
        <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
      </div>
      {open && (
        <div
          id="combobox-list"
          role="listbox"
          className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-popover p-1 shadow-md"
        >
          {filtered.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">
              {emptyText || "No results"}
            </p>
          ) : (
            filtered.map((opt) => (
              <button
                key={opt.value}
                type="button"
                role="option"
                aria-selected={opt.value === value}
                onClick={() => handleSelect(opt.value)}
                className={cn(
                  "relative flex w-full cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
                  "hover:bg-accent hover:text-accent-foreground",
                  opt.value === value && "bg-accent text-accent-foreground",
                )}
              >
                <div className="flex-1 min-w-0">
                  <span className="font-medium">{opt.label}</span>
                  {opt.subtitle && (
                    <span className="ms-2 text-xs text-muted-foreground">{opt.subtitle}</span>
                  )}
                </div>
                {opt.value === value && (
                  <Check className="h-4 w-4 shrink-0 text-primary ms-2" />
                )}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  )
}
