import { createFileRoute } from "@tanstack/react-router"
import MainChat from "@/components/Chat/MainChat"

export const Route = createFileRoute("/_certification/")({
  component: MainChat,
})