// المسار: src/features/admin/components/UsersTable.tsx
'use client';
import * as React from "react"
import {
ColumnDef,
flexRender,
getCoreRowModel,
useReactTable,
getPaginationRowModel,
} from "@tanstack/react-table"
import { useAdminUsers } from "../hooks/useAdminUsers"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import type { User } from '@/store/authStore';

// تعريف أعمدة الجدول
 export const columns: ColumnDef<User>[] = [
   { accessorKey: "id", header: "ID" },
   { accessorKey: "full_name", header: "الاسم الكامل" },
   { accessorKey: "email", header: "البريد الإلكتروني" },
   { 
       accessorKey: "is_admin", 
       header: "الدور",
       cell: ({ row }) => (
           <Badge variant={row.getValue("is_admin") ? "default" : "secondary"}>
               {row.getValue("is_admin") ? "مسؤول" : "مستخدم"}
           </Badge>
       ),
   },
 ]

 export function UsersTable() {
   const { data: users, isLoading, isError } = useAdminUsers();
   
   const table = useReactTable({
     data: users || [],
     columns,
     getCoreRowModel: getCoreRowModel(),
     getPaginationRowModel: getPaginationRowModel(),
   })

   if (isLoading) {
     return (
         <div className="space-y-2">
             <Skeleton className="h-10 w-full" />
             <Skeleton className="h-10 w-full" />
             <Skeleton className="h-10 w-full" />
         </div>
     );
   }
   
   if (isError) {
     return <div className="text-destructive">فشل في جلب بيانات المستخدمين.</div>
   }

   return (
     <div>
         <div className="rounded-md border">
         <Table>
             <TableHeader>
             {table.getHeaderGroups().map((headerGroup) => (
                 <TableRow key={headerGroup.id}>
                 {headerGroup.headers.map((header) => {
                     return (
                     <TableHead key={header.id}>
                         {header.isPlaceholder
                         ? null
                         : flexRender(
                             header.column.columnDef.header,
                             header.getContext()
                             )}
                     </TableHead>
                     )
                 })}
                 </TableRow>
             ))}
             </TableHeader>
             <TableBody>
             {table.getRowModel().rows?.length ? (
                 table.getRowModel().rows.map((row) => (
                 <TableRow
                     key={row.id}
                     data-state={row.getIsSelected() && "selected"}
                 >
                     {row.getVisibleCells().map((cell) => (
                     <TableCell key={cell.id}>
                         {flexRender(cell.column.columnDef.cell, cell.getContext())}
                     </TableCell>
                     ))}
                 </TableRow>
                 ))
             ) : (
                 <TableRow>
                 <TableCell colSpan={columns.length} className="h-24 text-center">
                     لا توجد نتائج.
                 </TableCell>
                 </TableRow>
             )}
             </TableBody>
         </Table>
         </div>
         <div className="flex items-center justify-end space-x-2 py-4">
            <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
            >
                السابق
            </Button>
            <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
            >
                التالي
            </Button>
        </div>
     </div>
   )
 }