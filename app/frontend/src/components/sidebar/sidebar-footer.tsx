import React from "react";
import { MoomooConnect } from "../ui/moomoo-connect";
import { Separator } from "../ui/separator";

export function SidebarFooter() {
  return (
    <div className="p-4 border-t border-ramp-grey-700">
      <Separator className="my-2" />
      <div className="flex flex-col gap-2">
        <MoomooConnect />
      </div>
    </div>
  );
}
