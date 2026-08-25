'use client';

import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Database, Table2, CheckCircle, XCircle, HardDrive, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';

interface ColumnInfo {
  name: string;
  type: string;
  notnull: boolean;
  pk: boolean;
}

interface TableInfo {
  table: string;
  rows: number;
  columns: ColumnInfo[];
}

interface DbInspectorData {
  database: string;
  size_bytes: number;
  size_formatted: string;
  wal_mode: boolean;
  integrity_check: boolean;
  total_tables: number;
  tables: TableInfo[];
}

export default function DbInspectorPage() {
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery<DbInspectorData>({
    queryKey: ['dbInspector'],
    queryFn: async () => { const res = await apiClient.get('/admin/db-inspector'); return res.data; },
    refetchInterval: 30_000,
  });

  if (isLoading) return <div className="flex min-h-[60vh] items-center justify-center"><div className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary" /></div>;

  const filteredTables = (data?.tables || []).filter(
    (t) => t.table.toLowerCase().includes(search.toLowerCase())
  );
  const selected = data?.tables.find((t) => t.table === selectedTable);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Database Inspector</h1>
        <p className="text-sm text-muted-foreground mt-1">Browse database schema, tables, and row counts</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Size</CardTitle>
            <HardDrive className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.size_formatted || '—'}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Tables</CardTitle>
            <Table2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data?.total_tables ?? 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Integrity</CardTitle>
            {data?.integrity_check ? <CheckCircle className="h-5 w-5 text-emerald-500" /> : <XCircle className="h-5 w-5 text-destructive" />}
          </CardHeader>
          <CardContent>
            <Badge variant={data?.integrity_check ? 'success' : 'destructive'}>
              {data?.integrity_check ? 'Passed' : 'Failed'}
            </Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">WAL Mode</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Badge variant={data?.wal_mode ? 'success' : 'secondary'}>
              {data?.wal_mode ? 'Enabled' : 'Disabled'}
            </Badge>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Tables</CardTitle>
            <CardDescription>{filteredTables.length} of {data?.total_tables} tables</CardDescription>
            <Input
              placeholder="Search tables..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="max-w-sm mt-2"
            />
          </CardHeader>
          <CardContent className="p-0">
            <div className="max-h-[60vh] overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Table</TableHead>
                    <TableHead>Rows</TableHead>
                    <TableHead>Columns</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTables.map((t) => (
                    <TableRow
                      key={t.table}
                      className={`cursor-pointer ${selectedTable === t.table ? 'bg-primary/5' : ''}`}
                      onClick={() => setSelectedTable(t.table)}
                    >
                      <TableCell className="font-mono text-sm">{t.table}</TableCell>
                      <TableCell>{t.rows.toLocaleString()}</TableCell>
                      <TableCell>{t.columns.length}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{selected ? selected.table : 'Table Schema'}</CardTitle>
            <CardDescription>
              {selected ? `${selected.columns.length} columns, ${selected.rows.toLocaleString()} rows` : 'Click a table to view its schema'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {selected ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Column</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Nullable</TableHead>
                    <TableHead>PK</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {selected.columns.map((col) => (
                    <TableRow key={col.name}>
                      <TableCell className="font-mono text-sm">{col.name}</TableCell>
                      <TableCell><code className="rounded bg-muted px-2 py-0.5 text-xs">{col.type}</code></TableCell>
                      <TableCell>{col.notnull ? '—' : '✅'}</TableCell>
                      <TableCell>{col.pk ? '🔑' : '—'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="flex items-center justify-center py-12 text-muted-foreground">
                <Search className="h-8 w-8 me-2" />
                Select a table to inspect
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
