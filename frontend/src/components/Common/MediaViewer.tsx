import { Download, X, ZoomIn, ZoomOut } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { cn } from "@/lib/utils"

interface MediaViewerProps {
  src: string
  alt?: string
  type: "image" | "pdf"
  className?: string
  thumbnailClassName?: string
}

export function MediaViewer({
  src,
  alt = "Media",
  type,
  className = "",
  thumbnailClassName = "",
}: MediaViewerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [zoom, setZoom] = useState(100)

  const handleDownload = () => {
    const link = document.createElement("a")
    link.href = src
    link.download = alt || "download"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 25, 200))
  }

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 25, 50))
  }

  const renderThumbnail = () => {
    if (type === "image") {
      return (
        <img
          src={src}
          alt={alt}
          className={cn(
            "h-32 w-32 cursor-pointer rounded-md border object-cover hover:opacity-80 transition-opacity",
            thumbnailClassName,
          )}
          onClick={() => setIsOpen(true)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              setIsOpen(true)
            }
          }}
          role="button"
          tabIndex={0}
        />
      )
    }
    return (
      <button
        type="button"
        className={cn(
          "flex h-32 w-32 cursor-pointer items-center justify-center rounded-md border bg-muted hover:bg-muted/80 transition-colors",
          thumbnailClassName,
        )}
        onClick={() => setIsOpen(true)}
      >
        <div className="flex flex-col items-center gap-2 text-muted-foreground">
          <svg
            className="h-8 w-8"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-label="PDF icon"
          >
            <title>PDF Document</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
            />
          </svg>
          <span className="text-xs font-medium">PDF</span>
        </div>
      </button>
    )
  }

  const renderViewer = () => {
    if (type === "image") {
      return (
        <div className="relative flex items-center justify-center p-4">
          <img
            src={src}
            alt={alt}
            style={{ transform: `scale(${zoom / 100})` }}
            className="max-h-[80vh] max-w-full object-contain transition-transform"
          />
        </div>
      )
    }
    return (
      <div className="h-[80vh] w-full">
        <iframe
          src={src}
          title={alt}
          className="h-full w-full border-0"
          style={{
            transform: `scale(${zoom / 100})`,
            transformOrigin: "top left",
          }}
        />
      </div>
    )
  }

  return (
    <>
      <div className={className}>{renderThumbnail()}</div>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] p-0">
          <div className="flex items-center justify-between border-b p-4 bg-muted/40">
            <h3 className="text-lg font-semibold">{alt}</h3>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="icon"
                onClick={handleZoomOut}
                disabled={zoom <= 50}
              >
                <ZoomOut className="h-4 w-4" />
              </Button>
              <span className="min-w-[4rem] text-center text-sm font-medium">
                {zoom}%
              </span>
              <Button
                variant="outline"
                size="icon"
                onClick={handleZoomIn}
                disabled={zoom >= 200}
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={handleDownload}>
                <Download className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setIsOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="overflow-auto">{renderViewer()}</div>
        </DialogContent>
      </Dialog>
    </>
  )
}
